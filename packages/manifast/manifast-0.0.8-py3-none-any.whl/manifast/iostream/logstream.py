#!/usr/bin/env python3
# coding=utf-8
'''
brief        :  
Author       : knightdby knightdby@163.com
Date         : 2023-04-04 15:20:13
FilePath     : /manifast/manifast/iostream/logstream.py
Description  : 
LastEditTime : 2023-04-06 10:01:32
LastEditors  : knightdby
Copyright (c) 2023 by Inc, All Rights Reserved.
'''

from loguru import logger


def logger_init():
    logger.add('runtime_{time}.log', rotation="500 MB")


def LOG_INFO(msg):
    logger.info(msg)


def LOG_WARNING(msg):
    logger.warning(msg)


def LOG_ERROR(msg):
    logger.error(msg)


if __name__ == '__main__':
    LOG_INFO('start')
    LOG_WARNING('start')
    LOG_ERROR('start')
    new_level = logger.level("SNAKY", no=38, color="<yellow>", icon="🐍")
    logger.log("SNAKY", "Here we go!")
