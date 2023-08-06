#!/usr/bin/env python3
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-04-20 15:01:35
FilePath     : /manifast/manifast/iostream/envstream.py
Description  : 
LastEditTime : 2023-04-20 15:05:50
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''

'''
Ubuntu 避免与 ROS python 环境冲突：
conda deactivate
conda activate base 
conda config --set auto_activate_base false 
conda config --set auto_activate_base true
'''
'''
Conda 更换镜像源
# 生成配置文件 .condarc
conda config --set show_channel_urls yes
# 配置文件的目录是：~/.condarc
vim ~/.condarc
# 修改condarc内容
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
ssl_verify: true
'''
'''
创建conda 虚拟环境
conda create -n torch python=3.6 #创建python3.6的torch虚拟环境
activate torch #激活虚拟环境torch

#安装ipykernel模块
conda install ipykernel
# 或
conda install jupyter notebook 
python -m ipykernel install --user --name torch --display-name "torch" #进行配置

#删除虚拟环境
conda remove -n torch --all
# 清除jupyter安装核
jupyter kernelspec list # 查看安装的内核和位置
jupyter kernelspec remove z1 #如果不正确移除该名字的kernel（假设叫做z1）或者不想要该kernel直接移除
'''
'''
第三方基础库安装
python -m pip install --upgrade pip
pip install autopep8
pip install flake8
pip install tqdm
pip install progressbar
pip install Pillow
pip install opencv-python==4.2.0.32
pip install h5py==2.10.0
pip install pandas
pip install labelme==3.16.5
pip install matplotlib
conda install yaml
conda install easydict
'''


def install_pkg():
    pass
