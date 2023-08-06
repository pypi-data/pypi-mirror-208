# -*- coding: utf-8 -*-
from loguru import logger
import time 
import functools
import sys
import os
 
# 日志耗时装饰器
def logtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info('【%s】 took %.2f s' % (func.__name__, (end - start)))
        return res
    return wrapper 

'''
该日志不保存
'''
def lump_logs(guid,text):
    data_begin = f"\n-------------------- {guid} Begin --------------------\n\n"
    data_end = f"\n-------------------- {guid} End --------------------\n\n"
    logger.debug(f"{data_begin} {text} {data_end}")

##-------------------------------------------------------------------------------------------------- 
     
try:
    log_level = os.environ['LOG_LEVEL']
except KeyError:
    log_level = 3  # pylint: disable=invalid-name (C0103)
    
levels = {0: 'ERROR', 1: 'WARNING', 2: 'INFO', 3: 'DEBUG'}


def log(level=2, message="", use_color=False): 
    current_time = time.time()
    time_array = time.localtime(current_time)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    if log_level >= level:
        if use_color:
            print("\033[1;31;40m{} [{}]\t{}\033[0m".format(
                current_time, levels[level], message).encode("utf-8")
                  .decode("latin1"))
        else:
            print("{} [{}]\t{}".format(current_time, levels[
                level], message).encode("utf-8").decode("latin1"))
        sys.stdout.flush()


def debug(message="", use_color=False):
    log(level=3, message=message, use_color=use_color)


def info(message="", use_color=False):
    log(level=2, message=message, use_color=use_color)


def warning(message="", use_color=True):
    log(level=1, message=message, use_color=use_color)


def error(message="", use_color=True, exit=True):
    log(level=0, message=message, use_color=use_color)
    if exit:
        sys.exit(-1)