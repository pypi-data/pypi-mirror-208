#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 21:58:02
FilePath     : /manifast/manifast/iostream/processsing.py
Description  : 
LastEditTime : 2023-05-08 10:31:40
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
from multiprocessing import Pool
from tqdm import tqdm
from .logstream import LOG_INFO


def run(image_path):
    print(image_path, end='')
    return (image_path)


def run_multi_threading(data_list, func):
    '''
    description: 多线程运行函数
    param       {*} data_list 所要处理数据 list
    param       {*} func 处理单条数据函数
    return      {*} 单条数据函数的返回值 list
    '''

    LOG_INFO(f'Data_list size: {len(data_list)}')
    with Pool(processes=10) as p:
        processed_data_list = list(
            tqdm(p.imap(func, data_list), total=len(data_list), desc='run multithread'))
    return processed_data_list


if __name__ == '__main__':
    data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                 36, 37, 38, 39, 40, 41, 42, ]
    func = run_multi_threading(data_list, run)
    print(func)
