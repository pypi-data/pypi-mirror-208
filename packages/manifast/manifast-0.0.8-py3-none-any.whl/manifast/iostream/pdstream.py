#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 21:54:44
FilePath     : /manifast/manifast/iostream/pdstream.py
Description  : 
LastEditTime : 2023-04-04 15:04:06
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
import pandas as pd


def get_df_types(dataframe, key):
    '''
    description: 获取dataframe中某列key的所有类型
    param       {*} dataframe DF数据表
    param       {*} key 列名
    return      {*} 类型 list和类型数量
    '''
    return list(dataframe[[key]].drop_duplicates()[key]), len(list(dataframe[[key]].drop_duplicates()[key]))
