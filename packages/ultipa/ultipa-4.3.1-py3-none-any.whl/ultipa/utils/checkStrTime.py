# -*- coding: utf-8 -*-
import datetime

from dateutil.parser import parse


def is_valid_date(strdate):
    '''判断是否是一个有效的日期字符串'''
    try:
        dt = parse(strdate)
    except Exception as e:
        return False
