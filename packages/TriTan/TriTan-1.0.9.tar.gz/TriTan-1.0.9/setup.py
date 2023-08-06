import setuptools
from setuptools import setup, find_packages 

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name = "TriTan",      #这里是pip项目发布的名称
    version = "1.0.9",  #版本号，数值大的会优先被pip
    keywords = ["pip", "TriTan"],			# 关键字
    description = "An efficient triple non-negative matrix factorisation method for integrative analysis of single-cell multiomics data",	# 描述
    long_description =long_description,
    license = "MIT Licence",		# 许可证

    url = "https://github.com/maxxxxxxxin/TriTan",     #项目相关文件地址，一般是github项目地址即可
    author = "maxxxxxxxin",			# 作者
    author_email ="xin.ma@postgrad.manchester.ac.uk",

    packages =['TriTan'],
    python_requires=">=3.6",
    include_package_data = True,
    install_requires = ["numpy", "sklearn", "scipy","umap-learn","hdbscan","numexpr"]          #这个项目依赖的第三方库
)
