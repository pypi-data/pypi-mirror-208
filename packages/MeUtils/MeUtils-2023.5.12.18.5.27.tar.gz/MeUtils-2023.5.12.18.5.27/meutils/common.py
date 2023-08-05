#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : common
# @Time         : 2020/11/12 11:42 上午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  : 单向引用，避免循环引用

import io
import os
import gc
import re
import sys
import time
import types
from abc import abstractmethod

import wget
import zipfile
import joblib
import datetime
import operator
import inspect
import textwrap
import requests
import socket
import warnings
import argparse
import yaml
import fire
import itertools
import subprocess
import wrapt
import traceback
import multiprocessing
import base64
import typer
import shutil
import asyncio
import importlib
import random
import numpy as np
import pandas as pd
import textwrap
import sklearn
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

plt.rcParams['axes.unicode_minus'] = False
from typing import *
# from PIL import Image, ImageGrab

from pathlib import Path
from loguru import logger
from tqdm.auto import tqdm

tqdm.pandas()
from functools import reduce, lru_cache, partial
from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pydantic import BaseModel, Field
from pprint import pprint

from faker import Faker  # https://www.cnblogs.com/aichixigua12/p/13236092.html

fake_zh = Faker(locale='zh_CN')

# 第三方
from meutils.other.crontab import CronTab
from meutils.other.besttable import Besttable

# ME
from meutils._utils import *
from meutils.init.evn import *
from meutils.init.oo import O000OO0O0000OO00O
from meutils.decorators import decorator, args, singleton, timer
from meutils.hash_utils import murmurhash
from meutils.path_utils import get_module_path, get_resolve_path, sys_path_append, path2list, get_config
from meutils.cache_utils import ttl_cache, disk_cache

O000OO0O0000OO00O()
try:
    import dill as pickle
except ImportError:
    import pickle

try:
    import orjson as json  # dumps 结果是字节型

    json.dumps = partial(json.dumps, option=json.OPT_NON_STR_KEYS)

except ImportError:
    import json

try:
    from IPython.core.interactiveshell import InteractiveShell

    InteractiveShell.ast_node_interactivity = "all"  # 多行输出
except ImportError:
    pass

cli = typer.Typer(name="MeUtils CLI")
warnings.filterwarnings("ignore")

# 常量
CPU_NUM = os.cpu_count()
HOST_NAME = socket.getfqdn(socket.gethostname())
FONT = FontProperties(fname=get_resolve_path('./data/SimHei.ttf', __file__))

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as _st:
        _st.connect(('10.255.255.255', 1))
        HOST, PORT = _st.getsockname()
        LOCAL_HOST = HOST
except:
    LOCAL_HOST = HOST = '127.0.0.1'
    PORT = None

LOCAL = LOCAL_HOST == "127.0.0.1"


def _bar(current, total, width=100):
    """https://www.jb51.net/article/232232.htm"""

    i = int(current / total * 100)
    s = f"""\r{i}%|{"█" * (i // 5)}|"""
    print(s, end="", flush=True)
    # sys.stdout.flush()


wget.download = partial(wget.download, bar=_bar)


# image
# im = ImageGrab.grabclipboard() 获取剪切板的图片


class BaseConfig(BaseModel):
    """基础配置"""
    _path: str = None

    @classmethod
    def init(cls):
        """init from path[zk/yaml]"""
        assert cls._path is not None, "请指定 _path"
        return cls.parse_path(cls._path)

    @classmethod
    def parse_path(cls, path):
        if Path(path).is_file():
            return cls.parse_yaml(cls._path)
        else:
            return cls.parse_zk(cls._path)

    @classmethod
    def parse_yaml(cls, path):
        json = yaml.safe_load(Path(path).read_bytes())
        return cls.parse_obj(json)

    @classmethod
    def parse_zk(cls, path):
        from meutils.zk_utils import get_zk_config
        json = get_zk_config(path)
        return cls.parse_obj(json)

    @classmethod
    def parse_env(cls):
        return cls.parse_obj(os.environ)


class Main(object):
    """
    if __name__ == '__main__':
        "一大堆业务逻辑"
        class TEST(Main):

            @args
            def main(self, **kwargs):
                print(kwargs)


        TEST.cli()
    """

    @args
    def main(self, **kwargs):
        """重写入口函数
        可用BaseConfig控制参数类型
        """
        pass

    @classmethod
    def cli(cls):
        """命令行"""
        logger.debug(f'MAIN: {cls.__name__}')
        fire.Fire(cls)  # 不支持__init__参数


# limit memory
def limit_memory(memory=16):
    """
    :param memory: 默认限制内存为 16G
    :return:
    """
    import resource

    rsrc = resource.RLIMIT_AS
    # res_mem=os.environ["RESOURCE_MEM"]
    memlimit = memory * 1024 ** 3
    resource.setrlimit(rsrc, (memlimit, memlimit))
    # soft, hard = resource.getrlimit(rsrc)
    logger.info("memory limit as: %s G" % memory)


def magic_cmd(cmd='ls', parse_fn=lambda s: s, print_output=False):
    """

    :param cmd:
    :param parse_fn: lambda s: s.split('\n')
    :param print_output:
    :return:
    """
    cmd = ' '.join(cmd.split())
    status, output = subprocess.getstatusoutput(cmd)
    output = output.strip()

    logger.info(f"CMD: {cmd}")
    logger.info(f"CMD Status: {status}")

    if print_output:
        logger.info(f"CMD Output: {output}")

    return status, parse_fn(output)


def is_open(ip='88.01.012.01'[::-1], port=7000, timeout=1):
    """
        os.system(f"ping {'88.01.012.01'[::-1]} -c 1 -W 1 > IS_PRODUCT") == 0

    @param ip:
    @param port:
    @param timeout:
    @return:
    """
    if ':' in ip:
        ip, port = ip.split(':')

    socket.setdefaulttimeout(timeout)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False


def get_var_name(var):
    """获取变量字符串名
        a=1
        b=1
        c=1
        只会取 a, 因是通过 id 确定 key
    """
    _locals = sys._getframe(1).f_locals
    for k, v in _locals.items():
        if id(var) == id(v):  # 相同值可能有误判
            return k


def get_current_fn():
    """获取执行函数的函数名
        def f(): # f
            print(get_current_fn())
    @return:
    """
    # inspect.currentframe().f_back === sys._getframe().f_back
    # f_name = inspect.getframeinfo(inspect.currentframe().f_back)[2]  # 最外层

    f_name = sys._getframe(1).f_code.co_name  # sys._getframe(1) 外层 sys._getframe(0) 内层
    return f_name


def clear(ignore=('TYPE_CHECKING', 'logger', 'START_TIME', 'CPU_NUM', 'HOST_NAME', 'LOCAL_HOST', 'LOCAL')):
    """销毁全局变量
    TODO：可添加过滤规则
    """
    keys = []
    ignore = set(ignore)
    for key, value in globals().items():
        if key.startswith('_') or key in ignore:
            continue
        if callable(value) or value.__class__.__name__ == "module":
            continue
        keys.append(key)

    logger.debug("销毁全局变量: " + list4log(keys))
    for key in keys:
        del globals()[key]
    return keys


def any2list(l, type=str):
    if isinstance(l, type):
        l = [l]
    return l


def show_code(func):
    sourcelines, _ = inspect.getsourcelines(func)
    return textwrap.dedent("".join(sourcelines))


def file_replace(file, old, new):
    p = Path(file)
    _ = (
        p.read_text()
        .replace(old, new)
    )
    p.write_text(_)


def exec_callback(source, **namespace):
    """

    @param source:
    @param namespace: source 入参
    @return: 出参
    """
    namespace = namespace or {}
    exec(source, namespace)
    namespace.pop('__builtins__')
    return namespace  # output


if __name__ == '__main__':
    s = "import pandas as pd; output = pd.__version__"
    s = "import os; output = os.popen(cmd).read().split()"
    print(exec_callback(s, cmd='ls'))
    # with timer() as t:
    #     time.sleep(3)
    #
    # status, output = magic_cmd('ls')
    # print(status, output)
    #
    # d = {'a': 1, 'b': 2}
    # print(bjson(d))
    # print(BaseConfig.parse_obj(d))

    print(show_code(show_code))
    print(get_var_name(s))
