#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 20:55:47
FilePath     : /wheel/manifast/model_analysis/summary.py
Description  : 
LastEditTime : 2023-02-24 21:01:54
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''


import numpy as np
from tqdm import tqdm
import time
import torch
# from thop import profile
# from thop import clever_format


def model_visual(model):
    blank = ' '
    print('-----------------------------------------------')
    print('|   weight name   |        weight shape       |')
    print('-----------------------------------------------')

    for index, (key, w_variable) in enumerate(model.named_parameters()):
        if len(key) <= 60:
            key = key + (60 - len(key)) * blank
        w_variable_blank = ''
        if len(w_variable.shape) == 1:
            if w_variable.shape[0] >= 120:
                w_variable_blank = 8 * blank
            else:
                w_variable_blank = 9 * blank
        elif len(w_variable.shape) == 2:
            if w_variable.shape[0] >= 120:
                w_variable_blank = 2 * blank
            else:
                w_variable_blank = 3 * blank

        print('| {} | {}{} |'.format(key, w_variable.shape, w_variable_blank))
        key = 0
    print('-----------------------------------------------')


# def model_summary(model, inputs=[torch.randn(1, 3, 640, 480), torch.randn(1, 1, 640, 480)]):
#     if len(inputs) == 2:
#         flops, params = profile(model, inputs=(inputs[0], inputs[1]))
#     else:
#         flops, params = profile(model, inputs=(inputs[0],))
#     flops, params = clever_format([flops, params], "%.3f")

#     type_size = 1
#     print('-' * 90)
#     print('#Model: {} | Params: {} | FLOPs: {}'.format(
#         model._get_name(), params, flops))
    # print('-' * 90)


def summary(model, input):
    model_visual(model)
    # pytorch_total_params = sum(p.numel() for p in net.parameters())
    # print("Total number of parameters: %.3fM" % (pytorch_total_params / 1e6))
    model = model.cuda()
    model.eval()
    run_time = list()
    if type(input) is list or type(input) is tuple:
        input = [data.cuda() for data in input]
    else:
        input = input.cuda()
    # input = torch.randn(2, 3, height, width).cuda()
    # depth_im = torch.randn(2, 1, height, width).cuda()
    for i in tqdm(range(0, 100)):
        torch.cuda.synchronize()
        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.no_grad():
            output = model(input)  # , aucx=False)
        torch.cuda.synchronize()  # wait for mm to finish
        end = time.perf_counter()
        run_time.append(end - start)
    run_time.pop(0)
    # print('Mean running time is ', np.mean(run_time))
    FPS = 1 / np.mean(run_time)
    # model_summary(model, input)
    print('#Model: {} | Runtime: {:.2f}s | FPS: {:.2f}'.format(
        model._get_name(), np.mean(run_time), FPS))
    print('-' * 90)
