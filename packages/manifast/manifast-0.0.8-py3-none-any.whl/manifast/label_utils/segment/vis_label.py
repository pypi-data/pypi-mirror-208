#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 23:21:14
FilePath     : /manifast/manifast/label_utils/segment/vis_label.py
Description  : 
LastEditTime : 2023-02-25 22:17:11
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
import cv2
from vis_utils import draw_label
from manifast import *


def visMaskLabel(image_path, label_path, label2num_dict={}, color_map=None):
    image = readImageFilebyCv(image_path)
    label_img = readImageFilebyCv(label_path)
    if not label2num_dict:
        for i in range(np.max(label_img)+1):
            label2num_dict[str(i)] = i
    mask_img = draw_label(
        label_img,
        image[:, :, ::-1],
        list(label2num_dict.keys()), color_map)
    return mask_img


def visMaskDistribution():
    pass


if __name__ == "__main__":
    image_path = '/home/knight/waytous/dataset/minedatset/images/sence_0_000106.jpg'
    idlabel_path = image_path.replace(
        'images', 'labelIds').replace('.jpg', '.png')
    mask_img = visMaskLabel(image_path, idlabel_path)
    save_path = './tmp/seg/masked_img.jpg'
    makePathDirs(save_path)
    cv2.imwrite(save_path, mask_img[:, :, ::-1])
