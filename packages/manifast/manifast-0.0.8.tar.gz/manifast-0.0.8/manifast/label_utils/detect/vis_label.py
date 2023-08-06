#!/usr/bin/env python
# coding=utf-8
'''
brief        :
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 23:21:03
FilePath     : /manifast/manifast/label_utils/detect/vis_label.py
Description  :
LastEditTime : 2023-02-25 11:05:01
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''
from manifast import *
from convert_label import xywh2xyxy
import cv2
import random
import colorsys
import seaborn as sn


def drawBbox(image, bboxes, classes_name, show_label=True):
    num_classes = len(classes_name)
    image_h, image_w, _ = image.shape
    hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    random.seed(0)
    random.shuffle(colors)
    random.seed(None)

    have_classes = []

    out_boxes, out_scores, out_classes, num_boxes = bboxes
    for i in range(num_boxes[0]):
        if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes:
            continue
        coor = out_boxes[0][i]
        coor[0] = int(coor[0] * image_h)
        coor[2] = int(coor[2] * image_h)
        coor[1] = int(coor[1] * image_w)
        coor[3] = int(coor[3] * image_w)

        fontScale = 0.5
        score = out_scores[0][i]
        class_ind = int(out_classes[0][i])
        bbox_color = colors[class_ind]
        bbox_thick = int(0.6 * (image_h + image_w) / 600)
        c1, c2 = (int(coor[1]), int(coor[0])), (int(coor[3]), int(coor[2]))
        cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)

        if show_label:
            bbox_mess = '%s: %.2f' % (classes_name[class_ind], score)
            have_classes.append(classes_name[class_ind])
            t_size = cv2.getTextSize(
                bbox_mess, 0, fontScale, thickness=bbox_thick // 2)[0]
            c3 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
            cv2.rectangle(image, c1, (c3[0], c3[1]), bbox_color, -1)  # filled

            cv2.putText(image, bbox_mess, (c1[0], c1[1] - 2), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale, (0, 0, 0), bbox_thick // 2, lineType=cv2.LINE_AA)
    return image, have_classes


def visBoxLabel(image_path, txt_path, label2num_dict={}):
    '''
    description: 可视化 box 标签
    param       {*} image_path 图像路径
    param       {*} txt_path label 路径
    return      {*} 可视化图
    '''
    image = readImageFilebyCv(image_path)
    poses = readTxtFile(txt_path)
    if not label2num_dict:
        for i in range(30):
            label2num_dict[str(i)] = i
    out_scores = []
    out_boxes = []
    out_classes = []
    for line in poses:
        pos = [float(i) for i in line.split(' ')]
        # ['1' '0.724877' '0.309082' '0.073938' '0.086914']
        [box] = xywh2xyxy(np.array([pos[1:]]))
        out_scores.append(0.99)
        [xmin, ymin, xmax, ymax] = box
        box = [ymin, xmin, ymax, xmax]
        out_boxes.append(box)
        out_classes.append(int(pos[0]))
    bboxes = [out_boxes], [out_scores], [out_classes], [len(poses)]
    drawBbox(image, bboxes, classes_name=list(
        label2num_dict.keys()), show_label=True)
    return image


def visBoxDistribution(box_paths, save_path='./tmp/class_distri.jpg'):
    '''
    description: 可视化 box 概率分布图
    param       {*} box_paths label path list
    param       {*} save_path 结果保存路径
    return      {*} null
    '''
    boxs = []  # 标注框xywh/size
    classes_id = []  # 类别名的索引
    for file in tqdm(box_paths):
        with open(file, 'r') as f:
            for l in f.readlines():
                # ['11' '0.724877' '0.309082' '0.073938' '0.086914']
                line = l.split()
                classes_id.append([int(line[0])])
                boxs.append(list(map(float, line[1:])))
    shapes = np.array(boxs)
    ids = np.array(classes_id)
    labels = np.hstack((ids, shapes))

    c, b = labels[:, 0], labels[:, 1:].transpose()  # classes, boxes
    nc = int(c.max() + 1)  # number of classes
    x = pd.DataFrame(b.transpose(), columns=['x', 'y', 'width', 'height'])
    ful = pd.DataFrame(labels, columns=['class', 'x', 'y', 'width', 'height'])
    sn.pairplot(ful, corner=True, diag_kind='auto', kind='hist',
                diag_kws=dict(bins=50), plot_kws=dict(pmax=0.9))
    makePathDirs(save_path)
    plt.savefig(save_path, dpi=200)
    plt.show()


if __name__ == "__main__":
    image_path = '/home/knight/waytous/dataset/minedatset/images/sence_0_000106.jpg'
    txt_path = image_path.replace(
        'images', 'labelBoxs').replace('.jpg', '.txt')
    labeled_image = visBoxLabel(image_path, txt_path)
    save_path = './tmp/det/labeled_img.jpg'
    makePathDirs(save_path)
    cv2.imwrite(save_path, labeled_image[:, :, ::-1])
    # txt_paths = getFileList(
    #     '/home/knight/waytous/dataset/minedatset/labelBoxs', '.txt')
    # print(txt_paths[0])
    # visBoxDistribution(txt_paths)
