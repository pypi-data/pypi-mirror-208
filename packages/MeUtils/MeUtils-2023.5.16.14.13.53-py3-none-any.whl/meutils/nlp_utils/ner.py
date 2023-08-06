#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : pos_tagging
# @Time         : 2023/4/23 12:28
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from paddlenlp import Taskflow


@lru_cache()
class Ner(object):

    def __init__(self, mode='fast', batch_size=8, entity_only=False, device=None, filter_func=None):
        """

        :param mode:
            fast lac
            accurate 解语
        :param filter_func: lambda w2t: w2t[1].startswith(('n', 'PER')) # word2tag
        :param batch_size:
        :param entity_only:
        :param device:
        """
        self.batch_size = max(batch_size, 2)
        self.filter_func = filter_func

        self.task_flow = Taskflow(
            task='ner',
            mode=mode,
            device=device,
            batch_size=batch_size,
            entity_only=entity_only
        )

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        results = texts | xbar4iter(self.task_flow, self.batch_size)
        if self.filter_func:  # 每一条都过滤
            results = results | xmap_(lambda w2ts: w2ts | xfilter_(self.filter_func))

        return results if len(texts) > 1 else [results]

    # 名词标注 https://github.com/PaddlePaddle/PaddleNLP/blob/develop/docs/model_zoo/taskflow.md#%E8%A7%A3%E8%AF%AD%E7%9F%A5%E8%AF%86%E6%A0%87%E6%B3%A8
    # >>> from paddlenlp import Taskflow
    # >>> nptag = Taskflow("knowledge_mining", model="nptag")
    # >>> nptag("糖醋排骨")
    # [{'text': '糖醋排骨', 'label': '菜品'}]


if __name__ == '__main__':
    # print(Ner('accurate')(['周杰伦是个音乐家'] * 10))
    filter_func = lambda w2t: w2t[1].startswith(('n', 'PER'))
    print(Ner('fast', filter_func=filter_func)(['周杰伦是个音乐家'] * 2))  # 1 有bug
    print(Ner('fast')('周杰伦是个音乐家'))
