#!/usr/bin/env python
# coding=utf-8
'''
brief        :
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 23:40:06
FilePath     : /manifast/manifast/label_utils/segment/gen_split_data.py
Description  :
LastEditTime : 2023-02-25 22:17:04
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''

from manifast import *

from convert_utils import cropRotateBox, rotateImagebyHeightLonger


def genGTDatabase(image_path, idlabel_path, label2num_dict={}, save_crop_dir='./tmp/database/seg'):
    '''
    description: 生成ground truth database
    param       {*} image_path 图像路径
    param       {*} txt_path 标注路径
    param       {*} save_crop_dir 数据库保存路径
    return      {*} crop image path list
    '''
    image = readImageFilebyCv(image_path)
    img_name = os.path.basename(image_path)[:-4]
    label_img = readImageFilebyCv(idlabel_path)
    if not label2num_dict:
        for i in range(np.max(label_img)+1):
            label2num_dict[str(i)] = i
    for item in label2num_dict.items():
        mask = np.where(label_img == item[1], 1, 0)
        mask = np.array(mask, np.uint8)
        class_img = np.multiply(image, mask[:, :, np.newaxis])
        im, contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = {}
        for cidx, cnt in enumerate(contours):
            if cv2.contourArea(cnt) < 200:
                continue
            minAreaRect = cv2.minAreaRect(cnt)
            rectCnt = np.int64(cv2.boxPoints(minAreaRect))
            cnts[cidx] = (rectCnt[1][0]+rectCnt[3][0])/2
            cv2.polylines(img=class_img, pts=[rectCnt], isClosed=True, color=(
                0, 0, 255), thickness=3)
        sort_cnts = sorted(cnts.items(), key=lambda x: x[1])  # 对字典进行排序
        for idx, key in enumerate(sort_cnts):
            # if item[1]==6:
            #     if cv2.contourArea(contours[key[0]]) < 500:
            #         save_name='sml-'+img_name+f'{-cv2.contourArea(contours[key[0]])}'
            #     else:
            #         save_name=img_name
            # elif item[1]==14:
            #     if cv2.contourArea(contours[key[0]]) < 1500:
            #         save_name='sml-'+img_name+f'{-cv2.contourArea(contours[key[0]])}'
            #     else:
            #         save_name=img_name
            # else:
            #     save_name=img_name
            save_name = img_name
            minAreaRect = cv2.minAreaRect(contours[key[0]])
            rectCnt = np.int64(cv2.boxPoints(minAreaRect))
            wrap_img = cropRotateBox(contours[key[0]], class_img)
            rotate_img = rotateImagebyHeightLonger(wrap_img)
            save_path = os.path.join(save_crop_dir, item[0]+'/'+save_name+'_'+str(idx) +
                                     '.jpg')
            makePathDirs(save_path)
            cv2.imwrite(save_path, rotate_img[:, :, ::-1])


def genSplitData(dataset_dir, label_paths, dataset_name, model='train'):
    save_path = dataset_dir + \
        f"/data_info/{dataset_name}_{model}_list.txt"
    makePathDirs(save_path)
    with open(save_path, 'w') as f:
        pass
    for label_path in label_paths:
        label_name = os.path.basename(label_path)
        with open(save_path, 'a') as f:
            if os.path.exists(dataset_dir+'/images/'+label_name.replace('.png', '.jpg')):
                f.write('images/'+label_name.replace('.png', '.jpg')+' '
                        + 'labelIds/'+label_name+'\n')
            elif os.path.exists(dataset_dir+'/images/'+label_name):
                f.write('images/'+label_name+' '
                        + 'labelIds/'+label_name+'\n')
            else:
                pass


if __name__ == "__main__":
    image_path = '/home/knight/waytous/dataset/minedatset/images/sence_0_000106.jpg'
    idlabel_path = image_path.replace(
        'images', 'labelIds').replace('.jpg', '.png')
    genGTDatabase(image_path, idlabel_path)
