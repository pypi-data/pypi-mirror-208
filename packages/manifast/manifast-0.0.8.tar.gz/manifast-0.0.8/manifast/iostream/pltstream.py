#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 21:54:33
FilePath     : /manifast/manifast/iostream/pltstream.py
Description  : 
LastEditTime : 2023-04-09 12:32:18
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
import numpy as np
import matplotlib.pyplot as plt


def plt_distribut_hist(data_list, x_names, save_name, save_dir='./', x_label='Classes', y_label='Number of Anchors'):
    '''
    description: 绘制数据分布直方图
    param       {*} data_list 数据list(非频数)
    param       {*} x_names x 轴刻度值
    param       {*} save_name 直方图保存名称
    param       {*} x_label x 轴显示名称
    param       {*} y_label y 轴显示名称
    param       {*} save_dir 直方图保存路径
    return      {*} null
    '''

    rects = plt.hist(data_list, bins=np.linspace(
        0, len(set(data_list)), len(set(data_list)) + 1) - 0.5, rwidth=0.8)

    for idx in range(len(rects[0])):
        height = rects[0][idx]
        plt.text(rects[1][idx]+0.1, height*1.01, '%s' % int(height))

    plt.ylabel(y_label)
    plt.xticks(range(len(x_names)), x_names, rotation=45)
    plt.xlabel(x_label)
    plt.tight_layout(pad=0.5)
    plt.savefig(save_dir+save_name+'.png',
                dpi=300, bbox_inches='tight')
    plt.show()


def plt_command():
    # 不显示 xy 轴刻度值
    plt.tick_params(labelbottom=False, labelleft=False)
    # 减小 plt 中多幅 img 之间间距
    plt.tight_layout(pad=0.5)
    plt.savefig('./img.jpg',
                dpi=300, bbox_inches='tight')
