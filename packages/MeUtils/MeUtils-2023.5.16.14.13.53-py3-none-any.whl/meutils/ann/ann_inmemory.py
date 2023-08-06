#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : ann_inmemory
# @Time         : 2023/5/15 17:50
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import numpy as np

from meutils.pipe import *
from sklearn.metrics.pairwise import cosine_similarity

from meutils.np_utils import cosine_topk

match = cosine_topk
