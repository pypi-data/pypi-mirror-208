#!/usr/bin/env python
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-02-24 20:55:39
FilePath     : /manifast/manifast/model_utils/grad_cam.py
Description  : 
LastEditTime : 2023-02-25 09:18:34
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''

import numpy as np
import cv2
from torchvision.models import mobilenet_v3_small


def visCaminImage(img, mask):
    heatmap = cv2.applyColorMap(
        np.uint8(255*mask), cv2.COLORMAP_JET)  # 利用色彩空间转换将heatmap凸显
    heatmap = np.float32(heatmap)/255  # 归一化
    cam = heatmap + np.float32(img)  # 将heatmap 叠加到原图
    cam = cam / np.max(cam)
    # cv2.imwrite('GradCam_test.jpg', np.uint8(255 * cam))  # 生成图像

    cam = cam[:, :, ::-1]  # BGR > RGB
    return np.uint8(255*cam)


class GradCAM(object):
    """
    1: 网络不更新梯度,输入需要梯度更新
    2: 使用目标类别的得分做反向传播
    """

    def __init__(self, net, layer_name):
        self.net = net
        self.layer_name = layer_name
        self.feature = None
        self.gradient = None
        self.net.eval()
        self.handlers = []
        self._register_hook()

    def _get_features_hook(self, module, input, output):
        self.feature = output
#         print("feature shape:{}".format(output.size()))

    def _get_grads_hook(self, module, input_grad, output_grad):
        """
        :param input_grad: tuple, input_grad[0]: None
                                   input_grad[1]: weight
                                   input_grad[2]: bias
        :param output_grad:tuple,长度为1
        :return:
        """
        self.gradient = output_grad[0]

    def _register_hook(self):
        for (name, module) in self.net.named_modules():
            if name == self.layer_name:
                self.handlers.append(
                    module.register_forward_hook(self._get_features_hook))
                self.handlers.append(
                    module.register_backward_hook(self._get_grads_hook))

    def remove_handlers(self):
        for handle in self.handlers:
            handle.remove()

    def __call__(self, inputs, cls_num=39):
        """
        :param inputs: [1,3,H,W]
        :param cls_num: class id
        :return:
        """
        self.net.zero_grad()
        x, y = inputs
        output = self.net(x, y)  # [1,num_classes]
        if cls_num is None:
            cls_num = np.argmax(output.cpu().data.numpy())
        target = output[0][cls_num][0][0]

        target.backward()

        gradient = self.gradient[0].cpu().data.numpy()  # [C,H,W]
        weight = np.mean(gradient, axis=(1, 2))  # [C]

        feature = self.feature[0].cpu().data.numpy()  # [C,H,W]

        cam = feature * weight[:, np.newaxis, np.newaxis]  # [C,H,W]
        cam = np.sum(cam, axis=0)  # [H,W]
        cam = np.maximum(cam, 0)  # ReLU

        # 数值归一化
        cam -= np.min(cam)
        cam /= np.max(cam)
        # resize to 224*224
        cam = cv2.resize(cam, (640, 480))
        return cam


class GradCamPlusPlus(GradCAM):
    def __init__(self, net, layer_name):
        """
         description: 
         param       {*} net model模型
         param       {*} layer_name     
         return      {*}
        """
        super(GradCamPlusPlus, self).__init__(net, layer_name)

    def __call__(self, inputs, cls_num):
        """
        :param inputs: [1,3,H,W] 
        :param cls_num: class num
        :return:
        """
        self.feature = None
        self.gradient = None
        self.net.zero_grad()
        x, y = inputs
        h, w = x.shape[-2:]
        output = self.net(inputs)  # [1,num_classes]
        if cls_num is None:
            cls_num = np.argmax(output.cpu().data.numpy())

        target = output[0][0][cls_num][0][0]
#         print(target)
        target.backward()

        gradient = self.gradient[0].cpu().data.numpy()  # [C,H,W]
        gradient = np.maximum(gradient, 0.)  # ReLU
        indicate = np.where(gradient > 0, 1., 0.)  # 示性函数
        norm_factor = np.sum(gradient, axis=(1, 2))  # [C]归一化
        for i in range(len(norm_factor)):
            norm_factor[i] = 1. / \
                norm_factor[i] if norm_factor[i] > 0. else 0.  # 避免除零
        alpha = indicate * norm_factor[:, np.newaxis, np.newaxis]  # [C,H,W]

        # [C]  alpha*ReLU(gradient)
        weight = np.sum(gradient * alpha, axis=(1, 2))

        feature = self.feature[0].cpu().data.numpy()  # [C,H,W]

        cam = feature * weight[:, np.newaxis, np.newaxis]  # [C,H,W]
        cam = np.sum(cam, axis=0)  # [H,W]
        # cam = np.maximum(cam, 0)  # ReLU

        # 数值归一化
        cam -= np.min(cam)
        cam /= np.max(cam)
        # resize to 224*640
        cam = cv2.resize(cam, (w, h))
        return cam


def alyModelFeatureCam(image, model=mobilenet_v3_small(), feats=['ident1',
                                                                 'ident2',
                                                                 'ident3',
                                                                 'ident4',
                                                                 'ident5', ]):

    grad_cam = GradCamPlusPlus(
        net=model, layer_name='encoder_depth.layer4.2.act')
    mask = grad_cam(inputs=(image), cls_num=39)
    img = image.copy()
    img = np.float32(cv2.resize(img, (640, 480))) / 255.
    visCaminImage(img, mask)
