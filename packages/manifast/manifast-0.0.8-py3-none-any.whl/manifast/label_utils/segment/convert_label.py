#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 23:21:13
FilePath     : /manifast/manifast/label_utils/segment/convert_label.py
Description  : 
LastEditTime : 2023-02-25 22:16:31
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
import json
import numpy as np
from manifast import *


def label_to_onehot(label, colormap):
    """  
    Converts a segmentation label (H, W, C) to (H, W, K) where the last dim is a one  
    hot encoding vector, C is usually 1 or 3, and K is the number of class.  
    """
    semantic_map = []
    for colour in colormap:
        equality = np.equal(label, colour)
        class_map = np.all(equality, axis=-1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1).astype(np.float32)
    return semantic_map


def onehot_to_label(semantic_map, colormap):
    """  
    Converts a mask (H, W, K) to (H, W, C)  
    """
    x = np.argmax(semantic_map, axis=-1)
    colour_codes = np.array(colormap)
    label = np.uint8(colour_codes[x.astype(np.uint8)])
    return label


def onehot2mask(semantic_map):
    """  
    Converts a mask (K, H, W) to (H,W)  
    """
    _mask = np.argmax(semantic_map, axis=0).astype(np.uint8)
    return _mask


def mask2onehot(mask, num_classes):
    """  
    Converts a segmentation mask (H,W) to (K,H,W) where the last dim is a one  
    hot encoding vector  

    """
    semantic_map = [mask == i for i in range(num_classes)]
    return np.array(semantic_map).astype(np.uint8)


def convertLabel2LabelmeJson(image_path, json_path, label_save_path):
    '''
    description: 转为标准 Labelme 格式的标注Json文件
    param       {*} image_path 图像路径
    param       {*} json_path label 路径（.json）
    param       {*} label_save_path 标准 label 保存路径
    return      {*} mask 数量
    '''
    with open(json_path, 'r', encoding='utf-8') as load_f:
        label_content = json.load(load_f)
    json_dict = {"version": "4.6.0", "flags": {}, "shapes": [],
                 "imagePath": "", "imageData": None,
                 "imageHeight": 0, "imageWidth": 0}
    json_dict["imagePath"] = image_path
    json_dict["imageHeight"] = label_content['info']['height']
    json_dict["imageWidth"] = label_content['info']['width']
    label_mask_num = 0
    for obj in label_content['dataList']:
        label_mask_num += 1
        img_mark_inf = {"label": "", "line_color": None, "fill_color": None,
                        "points": [], "shape_type": "polygon", "flags": {}}
        img_mark_inf["label"] = obj['label']
        img_mark_inf["shape_type"] = obj['shapeType']
        img_mark_inf["label"] = obj['label']
        for point in obj['coordinates'][0]:
            img_mark_inf["points"].append(point)
        json_dict["shapes"].append(img_mark_inf)
    makePathDirs(label_save_path)
    with open(label_save_path, "w") as out_json:
        json.dump(json_dict, out_json, ensure_ascii=False, indent=2)
    return label_mask_num


def convertLabelJson2IdImage(json_path, label2num_dict):
    '''
    description: 将 json 标准文件转为 label image
    param       {*} json_path label 路径
    param       {*} label2num_dict label 和 id 对应关系 dict
    return      {*} 标签 image: labelIds
    '''
    jsondata = json.load(open(json_path))
    img = cv2.imread(os.path.join(
        os.path.dirname(json_path), jsondata['imagePath']))
    shapes = jsondata['shapes']
    gt_mask = np.zeros(img.shape, dtype='uint8')
    # 生成顺序，首先绘制sky天空，->背景土墙->道路->挡墙->其他标签
    # for i in shapes_raw:
    #     label = i['label']
    #     points = i['points']
    #     if label == 'sky':
    #         points = np.array(points).reshape(-1, 1, 2).astype(int)
    #         gt_mask = cv2.fillPoly(
    #             gt_mask, [points], label2num_dict[label])
    for i in shapes:
        label = i['label']
        points = i['points']
        if label == 'sky':
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            # 使用mask面积作为阈值，删除小面积的天空mask，将其还原为0
            # if cv2.contourArea(points) > (1920*100):
            gt_mask = cv2.fillPoly(
                gt_mask, [points], label2num_dict[label])
    for i in shapes:
        label = i['label']
        points = i['points']
        if label == 'backgroundwall':
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            gt_mask = cv2.fillPoly(
                gt_mask, [points], label2num_dict[label])
    # for i in shapes_raw:
    #     label = i['label']
    #     points = i['points']
    #     if label == 'Backgroundwall':
    #         points = np.array(points).reshape(-1, 1, 2).astype(int)
    #         gt_mask = cv2.fillPoly(
    #             gt_mask, [points], label2num_dict[label])
    for i in shapes:
        label = i['label']
        points = i['points']
        if label == 'road':
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            gt_mask = cv2.fillPoly(
                gt_mask, [points], (label2num_dict[label], 0, 0))
    # for i in shapes_raw:
    #     label = i['label']
    #     points = i['points']
    #     if label == 'Road':
    #         points = np.array(points).reshape(-1, 1, 2).astype(int)
    #         gt_mask = cv2.fillPoly(
    #             gt_mask, [points], (label2num_dict[label], 0, 0))
    for i in shapes:
        label = i['label']
        points = i['points']
        if label == 'retainingwall':
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            gt_mask = cv2.fillPoly(
                gt_mask, [points], (label2num_dict[label], 0, 0))
    # for i in shapes_raw:
    #     label = i['label']
    #     points = i['points']
    #     if label == 'retainingwall':
    #         points = np.array(points).reshape(-1, 1, 2).astype(int)
    #         gt_mask = cv2.fillPoly(
    #             gt_mask, [points], (label2num_dict[label], 0, 0))
    # for i in shapes_raw:
    #     label = i['label']
    #     points = i['points']
    #     if label not in ['Backgroundwall', 'retainingwall', 'Road', 'sky', 'rut']:
    #         points = np.array(points).reshape(-1, 1, 2).astype(int)
    #         gt_mask = cv2.fillPoly(
    #             gt_mask, [points], (label2num_dict[label], 0, 0))
    for i in shapes:
        label = i['label']
        points = i['points']
        if label not in ['backgroundwall', 'retainingwall', 'sky', 'road']:
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            gt_mask = cv2.fillPoly(
                gt_mask, [points], (label2num_dict[label], 0, 0))
    for i in shapes:
        label = i['label']
        points = i['points']
        if label == 'puddle':
            points = np.array(points).reshape(-1, 1, 2).astype(int)
            # if cv2.contourArea(points) > 15000:

            gt_mask = cv2.fillPoly(
                gt_mask, [points], (label2num_dict[label], 0, 0))
    return gt_mask


def convertLabelJson2RGBImage(json_path, label2num_dict):
    pass


def convertLabelIdImage2Json(json_path, label2num_dict):
    pass
