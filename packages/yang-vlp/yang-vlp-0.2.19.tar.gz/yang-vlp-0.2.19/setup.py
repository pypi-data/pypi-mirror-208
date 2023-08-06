import os, shutil
from setuptools import setup, find_packages

#移除构建的build文件夹
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(CUR_PATH, 'build')
if os.path.isdir(path):
    print('INFO del dir ', path) 
    shutil.rmtree(path)

setup(
    name = 'yang-vlp', #应用名
    version = '0.2.19',  #版本号
    description = 'Construction of visible light positioning model', 
    packages = find_packages(),  #包括在安装包内的Python包
    include_package_data = True, #启用清单文件MANIFEST.in,包含数据文件
    # exclude_package_data = {'docs':['1.txt']},  #排除文件
    install_requires = [#自动安装依赖
        'numpy>=1.19.0',
        'matplotlib>=3.5.0',
        'scipy>=1.8.0',
        'pandas>=1.3.0'
    ],
    author = 'yangwuju',
    author_email = '1424134319@qq.com',
    url = 'https://gitee.com/yangwuju/yang_vlp',
)


