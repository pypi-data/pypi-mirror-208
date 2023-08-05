#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : __init__.py
# @Time         : 2020/11/26 2:57 下午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  :
from meutils.pipe import *


class DB(object):

    def __init__(self, is_test=None):

        if is_test is None:
            if HOST_NAME.__contains__('local') or LOCAL:
                is_test = True

        self.is_test = is_test

    def redis(self, ips=None, password=None, batch=False):  # redis集群
        """
        # todo: 批量插入（[(k, v),]）or yield
        @param ips:
        @param password:
        @param batch:
        @return:
        """
        if self.is_test:
            return {}

        from rediscluster import RedisCluster  # pip install redis-py-cluster

        startup_nodes = [dict(zip(['host', 'port'], ip.split(':'))) for ip in ips]

        rc = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            password=password,
        )
        if batch:
            return rc.pipeline()  # DB().redis.execute()

        else:
            return rc


class Redis(object):
    """
    rc.delete
    rc.lpush('lpush', 'a', 'b') # ['b', 'a']
    rc.rpush('rpush', 'a', 'b') # ['a', 'b']
    rc.rpop

    rc.lrange('rpush', 0, 10)
    rc.lrange('lpush', 0, 10)

    rc.hset(name, key=None, value=None, mapping=None)
    rc.hget(name, key)
    rc.hmget(name, keys, *args)

    rc.sadd('sadd', 0)
    rc.smembers('sadd')

    rc.zadd('zadd', mapping={'a': 888, 'b': 1})
    rc.zrange('zadd', 0, 1000, desc=True)

    队列 https://www.cnblogs.com/arkenstone/p/7813551.html
    """

    def __init__(self, ips=None, password=None, decode_responses=False, ttl=3):

        if isinstance(ips, str):
            import redis

            self.rc = redis.Redis(
                *ips.split(':'),
                password=password,
                decode_responses=decode_responses
            )

        else:
            from rediscluster import RedisCluster

            startup_nodes = [dict(zip(['host', 'port'], ip.split(':'))) for ip in ips]

            self.rc = RedisCluster(
                startup_nodes=startup_nodes,
                password=password,
                decode_responses=decode_responses,  # get对象设置False decode
                skip_full_coverage_check=True,
            )

        self.rc.set_obj = self._set_obj
        self.rc.get_obj = self._get_obj

        # ttl
        cache_fn = ttl_cache(ttl, key=str)
        self.rc.get_ttl = cache_fn(self.rc.get)
        self.rc.hget_ttl = cache_fn(self.rc.hget)  # rc.hget(name, key)
        self.rc.get_obj_ttl = cache_fn(self._get_obj)

    @timer("RedisInsertData")
    def insert(self, values, insert_fn=lambda k, v, p: p.set(k, v)):
        with self.rc.pipeline(transaction=False) as p:  # 事务：原子性、一致性、隔离性、持久性

            _insert_fn = functools.partial(insert_fn, p=p)
            for v in tqdm(values):  # xJobs
                _insert_fn(*v)

            p.execute()

    def _set_obj(self, key, obj, ex=None, px=None, nx=False, xx=False, keepttl=False):
        self.rc.set(key, pickle.dumps(obj), ex, px, nx, xx, keepttl)  # dill/pickle

    def _get_obj(self, key, default=None):
        try:
            _ = self.rc.get(key)
            return pickle.loads(_) if _ else default

        except Exception as e:
            logger.error(e)


class SQL(object):

    def __init__(self, **kwargs):
        self.conn = None  # 重写

    def get_dataframe(self, sql, chunksize=None, **kwargs):
        return pd.read_sql(sql, self.conn, chunksize=chunksize, **kwargs)

    def set_dataframe(self, df: pd.DataFrame, table: str, if_exists='replace', index=False, chunksize=None, **kwargs):
        df.to_sql(table, self.conn, if_exists=if_exists, index=index, chunksize=chunksize, **kwargs)


class Sqlite(SQL):

    def __init__(self, db='test.db', **kwargs):
        super().__init__(**kwargs)

        import sqlite3
        self.conn = sqlite3.connect(db)
        self.sqlite_master = pd.read_sql('SELECT * from SQLITE_MASTER', self.conn)
        self.sqlite_version = pd.read_sql('SELECT SQLITE_VERSION()', self.conn)


class MySQL(SQL):
    def __init__(self, user, password, host, port, database, **kwargs):
        super().__init__(**kwargs)

        import pymysql
        self.conn = pymysql.connect(user=user, password=password, host=host, port=port, database=database)


__all__ = ['Redis', 'Sqlite', 'MySQL', 'DB']  # 限制 from meutils.db import *

if __name__ == '__main__':
    rc = Redis('9736:071.4.9.931'[::-1], password='b***e', decode_responses=True).rc

    rc.set('a', 'xxxx')

    print(rc.get('a'))
