#!/usr/bin/env python
# coding=utf-8
'''
brief        :
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 21:40:04
FilePath     : /manifast/manifast/iostream/imagestream.py
Description  :
LastEditTime : 2023-04-09 11:40:59
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''


import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def read_image_cv(path):
    '''
    description: 读取图像数据
    param       {*} path 图像路径
    return      {*} 图像数据
    '''

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def read_image_pillow(path):
    with open(path, "rb") as f:
        img = Image.open(f)
        return img.convert("RGB")


def cv2image_add_mask(img, mask):
    """
     description: 将彩色图像与mask相叠加
     param       {*} img h*w*c
     param       {*} mask h*w
     return      {*} 叠加效果图
    """
    if mask.ndim == 3:
        mask = mask.squeeze()  # 去掉batch維度
    mask = mask.astype(np.uint8)
    display_mask = np.zeros_like(img)
    display_mask[mask == 1, 0] = 255
    masked = cv2.add(img, np.zeros(
        np.shape(img), dtype=np.uint8), mask=mask)
    masked = cv2.addWeighted(img, 0.5, display_mask, 0.5, 0)
    return masked


def cv2image_add_text(img, text, left, top, textColor=(0, 255, 0), textSize=20, font="Times_New_Roman_Bold"):
    '''
    description: 绘制文字至cv 图像中
    param       {*} img 绘制图像
    param       {*} text 文字内容
    param       {*} left x 位置
    param       {*} top y 位置
    param       {*} textColor 字体颜色
    param       {*} textSize 字体大小
    param       {*} font 字体
    return      {*} 绘制文字之后的 cv 图像
    '''
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        font, textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
