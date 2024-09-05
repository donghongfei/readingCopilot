#!/usr/bin/env python
# -*- coding:utf-8 -*-
##
 # Copyright (C) 2018 All rights reserved.
 #   
 # @File log.py
 # @Author hongfei
 # @Version 1.0
 # @Date 2024-08-07
 #
 #
import logging
import os
import sys


# 重置日志句柄
def _reset_logging(log):
    for handler in log.handlers:
        handler.close()
        log.removeHandler(handler)
        del handler
    log.handlers.clear()
    log.propagate = False
    console_handle = logging.StreamHandler(sys.stdout)
    console_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    file_handle = logging.FileHandler("run.log", encoding="utf-8")
    file_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log.addHandler(file_handle)
    log.addHandler(console_handle)

def _get_logging():
    log = logging.getLogger("log")
    _reset_logging(log)
    # 根据当前环境配置日志级别
    log_level = logging.DEBUG if os.getenv('APP_ENV', 'development') == 'development' else logging.WARNING
    log.setLevel(log_level)
    return log

logging = _get_logging()