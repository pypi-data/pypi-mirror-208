#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : cache_utils
# @Time         : 2021/11/24 上午11:09
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://cachetools.readthedocs.io/en/stable/
"""
FIFO：First In、First Out，就是先进先出。

LFU：Least Frequently Used，就是淘汰最不常用的。

LRU：Least Recently Used，就是淘汰最久不用的。

MRU：Most Recently Used，与 LRU 相反，淘汰最近用的。

RR：Random Replacement，就是随机替换。

TTL：time-to-live 的简称，也就是说，Cache 中的每个元素都是有过期时间的，如果超过了这个时间，那这个元素就会被自动销毁。
如果都没过期并且 Cache 已经满了的话，那就会采用 LRU 置换算法来替换掉最久不用的，以此来保证数量。
"""
import math
import pickle
import hashlib
import numpy as np
import pandas as pd
import joblib

from typing import Iterable
from functools import lru_cache
from pathlib import Path
from joblib import Memory
from loguru import logger
from tqdm.auto import tqdm
from cachetools import cached, cachedmethod, LRUCache, RRCache, TTLCache as _TTLCache, keys

# ME
from meutils.decorators import decorator, singleton
from meutils.hash_utils import md5

TTLCache = lru_cache()(_TTLCache)


def _pickle(obj, file):
    with open(file) as f:
        pickle.dump(obj, f)


def map_cache():
    return cached({})


def ttl_cache(ttl=60, maxsize=1024, key=keys.hashkey):
    """https://cachetools.readthedocs.io/en/stable/

        @ttl_cache()
        @disk_cache()
        def fn(x):  # 多级缓存
            time.sleep(1)
            return x

    @param ttl:
    @param maxsize:
    @param key: key_fn = lambda *args, **kwargs: f"{args}{kwargs}" # todo: 长数组支持有问题
    @return:
    """

    return cached(TTLCache(maxsize, ttl), key=key)  # LRUCache


@decorator
def redis_cache(func, rc=None, ex=3, *args, **kwargs):
    """redis 缓存"""
    k = f"cache_{func.__name__}_{args}_{kwargs}"

    if k in rc:
        return pickle.loads(rc.get(k))
    else:
        logger.info(f"CacheKey: {k}")
        _ = func(*args, **kwargs)
        rc.set(k, pickle.dumps(_), ex=ex)
        return _


@decorator
def cache4df(func, db='cache.db', verbose=1, *args, **kwargs):
    """返回值是df"""
    import sqlite3
    conn = sqlite3.connect(db)
    tables = set(pd.read_sql(f'select * from sqlite_master', conn)['tbl_name'])

    k = f"cache_{func.__name__}_{args}_{kwargs}"
    if k in tables:
        return pd.read_sql(f'select * from `{k}`', conn)
    else:
        if verbose:
            logger.info(f"CacheKey: {k}")

        df = func(*args, **kwargs)
        df.to_sql(k, conn, if_exists='replace', index=False)
        return df


@decorator
def disk_cache(func, location='cachedir', maxsize=128, ttl=np.inf, *args, **kwargs):
    ttl_cache = _TTLCache(maxsize, ttl)  # 单例

    k = md5(f"cache_{func.__name__}_{args}_{kwargs}")
    output = Path(location) / Path(k) / '__output.pkl'

    if (ttl == np.inf or k in ttl_cache) and output.is_file():  # ttl=np.inf 不作key判断, 相当于maxsize无穷大
        # return joblib.load(output)
        return pickle.load(open(output, 'rb'))

    else:
        ttl_cache[k] = 0  # 更新cache

        logger.info(f"CacheKey: {k}")
        output.parent.mkdir(parents=True, exist_ok=True)
        _ = func(*args, **kwargs)
        # joblib.dump(_, output)
        pickle.dump(_, open(output, 'wb'))
        return _


def mecache(location='mecache', maxsize=128, ttl=np.inf):
    ttl_cache = TTLCache(maxsize, ttl)

    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):
        k = md5(f"cache_{func.__name__}_{args}_{kwargs}")
        output = Path(location) / Path(k) / '__output.pkl'
        if (ttl == np.inf or k in ttl_cache) and output.is_file():  # ttl=np.inf 不作key判断
            return joblib.load(output)
        else:
            _ = func(*args, **kwargs)

            ttl_cache[k] = 0  # 更新cache，值仅存在硬盘
            logger.info(f"CacheKey: {k}")
            output.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(_, output)
        return _

    return wrapper


@decorator
def joblib_cache(func, location='cachedir', ignore=None, compress=False, verbose=1, *args, **kwargs):
    """硬盘缓存

    @param func:
    @param location:
    @param ignore: 有时我们不希望因某些参数的改变而导致重新计算，例如调试标志。
        @memory.cache(ignore=['debug'])
        def my_func(x, debug=True):
            print('Called with x = %s' % x)
    @param compress:
    @param verbose:
    @param args:
    @param kwargs:
    @return:
    """
    memory = Memory(location=location, verbose=verbose, compress=compress)
    return memory.cache(func, ignore)(*args, **kwargs)


@decorator
def cache4batch(func, location='cachedir', verbose=1, *args, **kwargs):
    """disk_cache 存中存

        @disk_cache()
        def f(x):
            return x

        [1,2,3] | xmap_(f)

    @param func: 单条入参（转batch)
    @param location:
    @param verbose:
    @param args:
    @param kwargs:
    @return: 由单条输入转为可多条输入  # TODO 放弃，违背装饰器原则，改变了输入输出
    """

    @disk_cache(location=location)
    def wrap(batch):
        if isinstance(batch, Iterable) and not isinstance(batch, str):
            if verbose:
                batch = tqdm(batch, desc='miss')
            return list(map(wrap, batch))  # 递归
        return func(batch)  # 需支持单条输入

    return wrap(args[0])



if __name__ == '__main__':
    from meutils.pipe import *


    @timer()
    @pickle_cache(location='demo')
    def func(x):
        time.sleep(5)
        return x


    func(11)


    @disk_cache()
    def f(x):
        return x


    @ttl_cache()
    def f4batch(x_batch):
        return list(map(x_batch, f))
