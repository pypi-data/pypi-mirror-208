#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 15:48:13
FilePath     : /manifast/setup.py
Description  : 
LastEditTime : 2023-05-17 14:13:49
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''


from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'requirements.txt'), 'r', encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

# 读取readme文件
with open("README.md", "r", encoding='utf-8') as f:
    readme = f.read()
setup(
    name="manifast",  # 包名称
    version="0.0.8",  # 版本
    author="Knight",  # 包邮箱
    author_email="knightdby@163.com",  # 作者邮箱
    description="A small example package",  # 包描述
    license='MIT License',
    # 长描述，通常是readme ,打包到PiPy需要 。
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/knightdby/wheel",  # 项目URL
    install_requires=install_requires,
    python_requires=">=3.6,<3.11",
    packages=find_packages(),  # 项目中需要的包
    include_package_data=True,   # 自动打包文件夹内所有数据
)
