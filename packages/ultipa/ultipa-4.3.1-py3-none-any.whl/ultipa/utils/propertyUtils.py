# -*- coding: utf-8 -*-
# @Time    : 2023/1/16 11:06 上午
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : propertyUtils.py
from ultipa.types import ULTIPA
from typing import List


def isBasePropertyType(type: ULTIPA.CreatePropertyType):
	if type in [ULTIPA.CreatePropertyType.PROPERTY_STRING,
		ULTIPA.CreatePropertyType.PROPERTY_INT,
		ULTIPA.CreatePropertyType.PROPERTY_INT64,
		ULTIPA.CreatePropertyType.PROPERTY_UINT32,
		ULTIPA.CreatePropertyType.PROPERTY_UINT64,
		ULTIPA.CreatePropertyType.PROPERTY_FLOAT,
		ULTIPA.CreatePropertyType.PROPERTY_DOUBLE,
		ULTIPA.CreatePropertyType.PROPERTY_DATETIME,
		ULTIPA.CreatePropertyType.PROPERTY_TIMESTAMP,
		ULTIPA.CreatePropertyType.PROPERTY_TEXT]:
		return True
	return False

def propertyGet(type: ULTIPA.PropertyType):
	return type


def getPropertyTypesDesc(type:ULTIPA.CreatePropertyType,subTypes:List[ULTIPA.CreatePropertyType]):

	if type==ULTIPA.CreatePropertyType.PROPERTY_LIST:
		subType = subTypes[0]
		if isBasePropertyType(subType):
			return f"{subType}[]"


	return type
