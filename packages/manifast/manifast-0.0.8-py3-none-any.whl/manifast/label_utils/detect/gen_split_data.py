#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 23:40:00
FilePath     : /manifast/manifast/label_utils/detect/gen_split_data.py
Description  : 
LastEditTime : 2023-02-25 10:53:26
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
from convert_label import xywh2xyxy
from manifast import *
import numpy as np


def genGTDatabase(image_path, txt_path, num2label_dict={}, save_crop_dir='./tmp/database/det'):
    '''
    description: 生成ground truth database
    param       {*} image_path 图像路径
    param       {*} txt_path 标注路径
    param       {*} save_crop_dir 数据库保存路径
    return      {*} crop image path list
    '''
    im_pil = readImagFilebyPillow(image_path)
    poses = readTxtFile(txt_path)
    if not num2label_dict:
        classes = list(set([int(line.split()[0]) for line in poses]))
        for i in classes:
            num2label_dict[i] = str(i)
    width, height = im_pil.size
    i = 0
    crop_img_paths = []
    for l in poses:
        line = l.split()
        xywh = np.array(
            list(map(float, line[1:]))) * np.array([width, height, width, height])
        [xyxy] = xywh2xyxy(np.array([xywh]))
        crop_image_name = os.path.basename(image_path)
        new_name = crop_image_name.replace('.jpg', f'-{i}.jpg')
        new_path = os.path.join(
            save_crop_dir, num2label_dict[int(line[0])], new_name)
        makePathDirs(new_path)
        im_crop = im_pil.crop(xyxy)
        im_crop.save(new_path)
        crop_img_paths.append(new_path)
        i += 1
    return crop_img_paths


if __name__ == '__main__':
    image_path = '/home/knight/waytous/dataset/minedatset/images/sence_0_000106.jpg'
    txt_path = image_path.replace(
        'images', 'labelBoxs').replace('.jpg', '.txt')
    genGTDatabase(image_path, txt_path)
