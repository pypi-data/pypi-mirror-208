#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-25 09:28:57
FilePath     : /manifast/manifast/label_utils/segment/convert_utils.py
Description  : 
ref https://github.dev/guchengxi1994/mask2json
LastEditTime : 2023-02-25 10:17:05
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
import cv2
import numpy as np


def cropRotateBox(cnt, img):

    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    width = int(rect[1][0])
    height = int(rect[1][1])
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    warped = cv2.warpPerspective(img, M, (width, height))
    return warped


def rotateImagebyHeightLonger(img):
    h, w, _ = img.shape

    if h > w:
        '''getRotationMatrix2D only rotate kepp same ratio'''
        # cv2.getRotationMatrix2D出来的图特别小，是在原始图上截取的，
        # 也就是说要先对原图做padding，不然旋转后超出原始图像的像素会不被保留，所以最后改成了np.rot90
        # center = (w / 2, h / 2)
        # M = cv2.getRotationMatrix2D(center,90,1)
        # rotate_img = cv2.warpAffine(img,M,(w,h))
        # h_stack = np.hstack((img, rotate_img))
        rotate_img = np.rot90(img, 1)
        # cv2.imshow('img', rotate_img)
        # cv2.waitKey()
        return rotate_img
    else:
        return img
