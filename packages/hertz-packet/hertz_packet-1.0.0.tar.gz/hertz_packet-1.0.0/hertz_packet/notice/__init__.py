# -*- coding: utf-8 -*-

"""
@Project : hertz_packet 
@File    : __init__.py
@Date    : 2023/5/12 10:31:05
@Author  : zhchen
@Desc    : 
"""
import json

import requests


def send_note(_k, _v, _memo: dict = None):
    """发送键值对到数据库，用于分析情况"""
    try:
        data = {"key": _k, "value": _v, }
        if _memo:
            data['memo'] = json.dumps(_memo)
        requests.post(
            "https://note-tempnote-edzsrbkyef.cn-hangzhou.fcapp.run",
            json=data)
    except Exception:
        pass
