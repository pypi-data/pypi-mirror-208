# -*- coding: utf-8 -*-
"""
jf-ext.debugExt.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import time
from icecream import ic # noqa
from jfExt.CommonExt import get_latency_msg_for_millisecond


time_dict = {}

def debug_timeout_set_by_key(key):
    """
    >>> 调试: 延迟计算 - 设置起始点 by key
    :param {String} key:
    """
    time_dict[key] = time.time()


def debug_timeout_get_by_key(key):
    """
    >>> 调试: 延迟计算 - 获取 by key
    :param {String} key:
    """
    end_time = time.time()
    start_time = time_dict.get(key, None)
    # 未找到起始时间, 返货None
    if not start_time:
        return None
    proc_time = int((end_time - start_time) * 1000)
    msg = "🦞{}".format(get_latency_msg_for_millisecond(proc_time, key))
    print(msg)
    return msg


if __name__ == '__main__':
    debug_timeout_set_by_key("A")
    time.sleep(1.1113)
    debug_timeout_get_by_key("A")

