#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""

████████╗███████╗███████╗████████╗    ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗
╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝
   ██║   █████╗  ███████╗   ██║          ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝
   ██║   ██╔══╝  ╚════██║   ██║          ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗
   ██║   ███████╗███████║   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗
   ╚═╝   ╚══════╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝

    Test Toolbox | 测试工具箱 by Gavin
    
@Author    : Gavin
@DateTime  : 2021/6/9 09:56
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : setup.py
@Describe  : TestToolbox 测试工具箱 | 辅助快速测试与验证
————————————————————
@Version   : 1.0.1
"""
# update   : 0.1 调试
# 1. python setup.py develop
# 2. python setup.py sdist bdist_wheel
# ————————————————————
# update   : 05/14
# 1. python setup.py sdist upload
# 2. 
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————


from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ToolBox4Test",
    version="1.0.3",
    author="Gavin",
    author_email="guowenwhy@foxmail.com",
    description="TestToolbox 测试工具箱",
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # 项目主页
    url="https://gitlab.com/Gavinwhy/TestToolBox",
    
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),
    include_package_data=True,
    
    entry_points={
            'console_scripts': [
                'testbox = TestToolBox.toolbox:main'
            ]
        },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    
    install_requires=[
        'pyyaml>=6.0',
        'jsonpath>=0.82',
        'pycallgraph>=1.0.1',
        'pytest>=7.1.2',
        'selenium>=4.9.0',
        'faker>=13.3.2',
        'requests>=2.29.0',
        'xmind>=1.2.0',
        'loguru>=0.5.3',
        'pymysql>=1.0.2',
        'redis>=3.5.3',
        'business-rules-enhanced>=1.2.2'
    ]
)
