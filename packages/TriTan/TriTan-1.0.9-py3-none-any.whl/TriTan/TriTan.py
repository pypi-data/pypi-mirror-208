from sklearn.feature_extraction.text import TfidfTransformer 
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import normalize
from sklearn.utils.extmath import safe_sparse_dot
from sklearn.utils.extmath import randomized_svd

from scipy.sparse.linalg import svds
from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import inv
from scipy.spatial import cKDTree

from numpy.core.umath_tests import inner1d
from numpy.linalg import matrix_rank
import numexpr as ne
import numpy as np
import hdbscan
from umap.umap_ import UMAP


class TriTan():
    def __init__(self,
                n_modalities=2,
                n_clusters = 100,
                resolution=10,
                epoch =30,
                res_size=60,
                complexity=5,
                precomputed = False,
                svd_rna= None,
                svd_atac = None,
                sparse = False,
                n_component= [20,50,20,50]):

        self.clusters = n_clusters
        self.epoch=epoch
        self.complexity = complexity
        self.precomputed = precomputed
        if svd_rna is not None:
            self.svd_rna= svd_rna
        if svd_atac is not None:
            self.svd_atac= svd_atac
        self.sparse = sparse
        self.n_component=np.array(n_component)
        self.resolution=resolution
        self.res_size=res_size
        self.loss=[]
        self.loss_atac =[]
        self.loss_rna = []
        self.epoch_times =[]
    def fit(self,mdata):
        X_rna,X_atac = self.load(mdata)
        S_gene,S_atac,G_gene,G_atac,rank1,ww_gene,ww_atac = self.initialize_(X_rna,X_atac)
        iteration=0
        if self.precomputed:
            if self.svd_rna==None or self.svd_atac==None:
                raise ValueError('please input precomputed SVD =[u,vt]')
            else:
                u_rna, v_rna = self.svd_rna[0],self.svd_rna[1]
                u_atac, v_atac =self.svd_atac[0],self.svd_atac[1]
                C_rna,D_rna,C_atac,D_atac = self.prepocess_precompute(X_rna,X_atac,u_rna,v_rna,u_atac,v_atac)
        else:
            if self.sparse:
                X_rna,X_atac=self.load_sparse(mdata)
            else:
                X_rna,X_atac=self.load(mdata)
            
            u_rna,v_rna,u_atac,v_atac,C_rna,D_rna,C_atac,D_atac = self.prepocess(X_rna,X_atac)
   
        
        while True:
            rank1=self.resolution

            F,UU_gene,UU_atac = self.fit_F(C_rna,C_atac,v_rna,v_atac,
                                           S_gene,S_atac,G_gene,G_atac,
                                           ww_gene,ww_atac,rank1)
            G_gene,G_atac = self.fit_G(D_rna,D_atac,u_rna,u_atac,F,S_gene,S_atac)
            S_gene,S_atac = self.fit_S(X_rna,X_atac,F,G_gene,G_atac,rank1)
            c,c_gene,c_atac,ww_gene,ww_atac = self.ww(F,UU_gene,UU_atac,C_rna,C_atac)

            iteration+=1
            self.loss.append(c)
            self.loss_atac.append(c_atac)
            self.loss_rna.append(c_gene)
            if iteration >= 20:
                break
        C =np.concatenate((C_rna*ww_gene,C_atac*ww_atac), axis=1)
        reducer = UMAP()
        embedding = reducer.fit_transform(C)
        self.embedding =embedding
        self.F_rough = F
        F_new =self.subcluster(F,C_rna,C_atac,embedding)
        while True:
            n_f_rna = self.n_component[0]
            n_f_atac = self.n_component[2]
            S_gene,S_atac = self.fit_S(X_rna,X_atac,F_new,G_gene,G_atac,rank1)
            G_gene,G_atac = self.fit_G(D_rna,D_atac,u_rna,u_atac,F_new,S_gene,S_atac)
            U= S_gene@G_gene.T
            UU_gene = U@v_rna.T[:,0:n_f_rna]
            U = S_atac@G_atac.T
            UU_atac = U@v_atac.T[:,0:n_f_atac]
            c,c_gene,c_atac,ww_gene,ww_atac = self.ww(F_new,UU_gene,UU_atac,C_rna,C_atac)
            iteration+=1
            self.loss.append(c)
            self.loss_atac.append(c_atac)
            self.loss_rna.append(c_gene)
            if iteration >= self.epoch or np.abs(self.loss[iteration-1]-self.loss[iteration-2])<=0.1:
                break
        S_atac=S_atac[:,S_atac.sum(axis=0)!=0]
        S_gene=S_gene[:,S_gene.sum(axis=0)!=0]
        G_atac=G_atac[:,G_atac.sum(axis=0)!=0]
        G_gene=G_gene[:,G_gene.sum(axis=0)!=0]
        self.iteration = iteration
        self.F =F_new
        self.S_gene,self.S_atac,self.G_gene,self.G_atac = S_gene,S_atac,G_gene,G_atac
            
    def load_sparse(self,mdata):
        X_rna=mdata['rna'].X
        self.m,self.n_rna = X_rna.shape
        X_atac=mdata['atac'].X
        self.n_atac = X_atac[1]
        X_rna = csr_matrix(X_rna)
        X_atac = csr_matrix(X_atac)
        return X_rna,X_atac
    
    def load(self,mdata):
        X_rna=mdata['rna'].X
        self.m,self.n_rna = X_rna.shape
        X_atac=mdata['atac'].X
        self.n_atac = X_atac.shape[1]
        return X_rna,X_atac     
    def prepocess_precompute(self,X_rna,X_atac,u_rna,v_rna,u_atac,v_atac):
        n_f_rna = self.n_component[0]
        n_f_atac = self.n_component[2]
        n_g_rna = self.n_component[1]
        n_g_atac = self.n_component[3]
        C_rna = X_rna@v_rna.T[:,0:n_f_rna]
        D_rna = u_rna[:,0:n_g_rna].T@X_rna
        C_atac = X_atac@v_atac.T[:,0:n_f_atac]
        D_atac = u_atac[:,0:n_g_atac].T@X_atac
        C =np.concatenate((C_rna,C_atac), axis=1)
        reducer = UMAP()
        embedding = reducer.fit_transform(C)
        self.embedding =embedding
        return C_rna,D_rna,C_atac,D_atac
    def prepocess(self,X_rna,X_atac):
        n_f_rna = self.n_component[0]
        n_f_atac = self.n_component[2]
        n_g_rna = self.n_component[1]
        n_g_atac = self.n_component[3]
        maxcom=self.n_component.max()
        u_rna, s_rna, v_rna = randomized_svd(X_rna,n_components=maxcom, random_state=0)
        u_atac, s_atac, v_atac = randomized_svd(X_atac,n_components=maxcom, random_state=0)
        C_rna = X_rna@v_rna.T[:,0:n_f_rna]
        D_rna = u_rna[:,0:n_g_rna].T@X_rna
        C_atac = X_atac@v_atac.T[:,0:n_f_atac]
        D_atac = u_atac[:,0:n_g_atac].T@X_atac

        return u_rna,v_rna,u_atac,v_atac,C_rna,D_rna,C_atac,D_atac
    def initialize_(self,X_rna,X_atac):
        n_rna,n_atac = self.n_rna,self.n_atac
        max_gene = X_rna.max()
        max_atac = X_atac.max()
        rank1 = self.resolution
        ww_gene=1/2
        ww_atac=1/2
        rank2 = self.clusters
        S_gene = np.random.uniform(0,max_gene,[rank1,rank2])
        S_atac = np.random.uniform(0,max_atac,[rank1,rank2])
        G_gene = np.random.uniform(0,max_gene,[n_rna,rank2])
        G_atac = np.random.uniform(0,max_atac,[n_atac,rank2])
        return S_gene,S_atac,G_gene,G_atac,rank1,ww_gene,ww_atac
    def np_pearson_cor(self,x, y):
        xv = x - x.mean(axis=0)
        yv = y - y.mean(axis=0)
        xvss = (xv * xv).sum(axis=0)
        yvss = (yv * yv).sum(axis=0)
        result = np.matmul(xv.transpose(), yv) / np.sqrt(np.outer(xvss, yvss))
        # bound the values to -1 to 1 in the event of precision issues
        return np.maximum(np.minimum(result, 1.0), -1.0)
    def fit_F(self,C_rna,C_atac,v_rna,v_atac,S_gene,S_atac,G_gene,G_atac,ww_gene,ww_atac,rank1):
        n_f_rna = self.n_component[0]
        n_f_atac = self.n_component[2]
        m=self.m
        comp =self.complexity
        index_m =np.array([i for i in range(m)])
        
        F_gene = np.zeros([m,rank1])
        F_atac = np.zeros([m,rank1])
        U= S_gene@G_gene.T
        UU_gene = U@v_rna.T[:,0:n_f_rna]
        t = cKDTree(UU_gene).query(C_rna, k=comp,workers=-1)[1]
        p = self.np_pearson_cor(C_rna.T,UU_gene.T)
        z=[]
        for i in range(m):
            y =np.argmax(np.abs(p[i])[t[i]],axis=0)
            z.append(t[i][y])
        F_gene[index_m,z]=1

        U = S_atac@G_atac.T
        UU_atac = U@v_atac.T[:,0:n_f_atac]
        t = cKDTree(UU_atac).query(C_atac, k=comp,workers=-1)[1]
        p = self.np_pearson_cor(C_atac.T,UU_atac.T)
        z=[]
        for i in range(m):
            y =np.argmax(np.abs(p[i])[t[i]],axis=0)
            z.append(t[i][y])
        F_atac[index_m,z]=1
        F = F_gene*ww_gene+F_atac*ww_atac
        return F,UU_gene,UU_atac
    def fit_G(self,D_rna,D_atac,u_rna,u_atac,F,S_gene,S_atac):
        n_g_rna = self.n_component[1]
        n_g_atac = self.n_component[3]
        n_rna,n_atac = self.n_rna,self.n_atac
        comp =self.complexity
        rank2 = self.clusters        
        index_n_atac =np.array([i for i in range(n_atac)])
        index_n_gene =np.array([i for i in range(n_rna)])

        
        V = F@S_gene
        VV = u_rna[:,0:n_g_rna].T@V
        G_gene = np.zeros([n_rna,rank2])
        k = cKDTree(VV.T).query(D_rna.T, k=comp,workers=-1)[1]
        p = self.np_pearson_cor(D_rna,VV)
        z=[]
        for i in range(n_rna):
            y =np.argmax(np.abs(p[i])[k[i]],axis=0)
            z.append(k[i][y])
        G_gene[index_n_gene,z]=1

        V = F@S_atac
        VV = u_atac[:,0:n_g_atac].T@V
        G_atac = np.zeros([n_atac,rank2])
        k = cKDTree(VV.T).query(D_atac.T, k=comp,workers=-1)[1]
        p = self.np_pearson_cor(D_atac,VV)
        z=[]
        for i in range(n_atac):
            y =np.argmax(np.abs(p[i])[k[i]],axis=0)
            z.append(k[i][y])
        G_atac[index_n_atac,z]=1

        return G_gene,G_atac
    
    def fit_S(self,X_gene,X_atac,F,G_gene,G_atac,rank1):
        rank2=self.clusters
        enum = np.linalg.pinv(F.T@F)
        denom = np.linalg.pinv(G_gene.T@G_gene)
        S_gene = enum@F.T@X_gene@G_gene@denom
        denom = np.linalg.pinv(G_atac.T@G_atac)
        S_atac = enum@F.T@X_atac@G_atac@denom
        return S_gene,S_atac
    
    def ww(self,F,UU_gene,UU_atac,C_rna,C_atac):
        soft_matrix_gene = F@UU_gene
        soft_matrix_atac = F@UU_atac
        p = C_rna - soft_matrix_gene
        q = C_atac - soft_matrix_atac
        cc = np.mean(np.abs(p),axis=1)/np.mean(np.abs(q),axis=1)
        w_gene = inner1d(p,p)
        m_atac = inner1d(q,q)
        w_atac = cc*m_atac
        ww_gene = w_atac/(w_gene+w_atac)
        ww_atac = w_gene/(w_gene+w_atac)
        ww_gene = np.expand_dims(ww_gene, 1)
        ww_atac = np.expand_dims(ww_atac, 1)
        c_gene = np.sum(w_gene)
        c_atac = np.sum(m_atac)
        c = c_gene+c_atac
        return c,c_gene,c_atac,ww_gene,ww_atac
    
    def subcluster(self,F,C_rna,C_atac,umap_embedding):
        m = self.m
        index_m =np.array([i for i in range(m)])
        group=np.argmax(F.T, axis =0)
        new=np.zeros(m,dtype=int)       
        nl=[]
        nl.append(0)
        for i in range(self.resolution):
            k = len(group[group==i])
            embedding=umap_embedding[group==i,:]
            clusterer = hdbscan.HDBSCAN(min_cluster_size=self.res_size).fit(embedding)
            u=np.unique(clusterer.labels_)
            n=len(u)
            if np.all(clusterer.labels_==-1):
                new[group==i]= nl[i-1]
            else:
                clusterer.labels_[clusterer.labels_==-1]=-100
                new[group==i]=clusterer.labels_+np.sum(nl)+1       
            nl.append(n)  
        new[new<0]=0
        rank1 = np.sum(nl)
        F_new=np.zeros([m,rank1])
        F_new[index_m,new]=1
        F_new = F_new[:,~np.all(F_new==0, axis = 0)]
        ii = np.argmax(F_new.T,axis =0)
        rank1 = len(np.unique(ii))
        rank2 = C_rna.shape[1]
        out_gene=C_rna[ii==0,:]
        out_atac=C_atac[ii==0,:]
        UU_gene = np.zeros([rank1-1,rank2])
        UU_atac = np.zeros([rank1-1,rank2])
        out =np.concatenate((out_gene,out_atac), axis=1)
        for i in range(len(np.unique(ii))-1):
            UU_gene[i,:]=(np.mean(C_rna[ii==i+1,:],axis=0))
            UU_atac[i,:]=(np.mean(C_atac[ii==i+1,:],axis=0))
        UU=np.concatenate((UU_gene,UU_atac), axis=1)
        t = cKDTree(UU).query(out, k=1,workers=-1)[1]
        F_new[ii==0,t+1]=1
        F_new = F_new[:,~np.all(F_new==0, axis = 0)]
        F_new=F_new[:,1:]
        return F_new