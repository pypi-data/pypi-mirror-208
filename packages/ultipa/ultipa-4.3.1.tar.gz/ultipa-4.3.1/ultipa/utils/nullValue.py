# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 9:45 上午
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : null.py
import sys
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils.errors import ParameterException, ServerException, SerializeException, checkError


StringNull = bytes([0x00])
Int32Null = bytes([0x7f,0xff,0xff,0xff])
Uint32Null =bytes([0xff,0xff,0xff,0xff])
Int64Null = bytes([0x7f,0xff,0xff,0xff,0xff,0xff,0xff,0xff])
Uint64Null = bytes([0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff])
FloatNull = bytes([0xff,0xff,0xff,0xff])
DoubleNull = bytes([0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff])
PointNull = bytes([0x6e,0x75,0x6c,0x6c])

def nullValue(type:ULTIPA.PropertyType):
	if type in [ULTIPA.PropertyType.PROPERTY_STRING,ULTIPA.PropertyType.PROPERTY_TEXT]:
		return StringNull
	elif type == ULTIPA.PropertyType.PROPERTY_INT32:
		return Int32Null
	elif type == ULTIPA.PropertyType.PROPERTY_UINT32:
		return Uint32Null
	elif type == ULTIPA.PropertyType.PROPERTY_INT64:
		return Int64Null
	elif type == ULTIPA.PropertyType.PROPERTY_UINT64:
		return Uint64Null
	elif type == ULTIPA.PropertyType.PROPERTY_FLOAT:
		return FloatNull
	elif type == ULTIPA.PropertyType.PROPERTY_DOUBLE:
		return DoubleNull
	elif type == ULTIPA.PropertyType.PROPERTY_DATETIME:
		return Uint64Null
	elif type == ULTIPA.PropertyType.PROPERTY_TIMESTAMP:
		return Uint32Null
	elif type == ULTIPA.PropertyType.PROPERTY_POINT:
		return PointNull
	elif type in [ULTIPA.PropertyType.PROPERTY_LIST,ULTIPA.PropertyType.PROPERTY_SET]:
		return None
	raise SerializeException(f"not support [{ULTIPA_REQUEST.Property.PropertyReverseMap.get(type)}]")

def isNullValue(v: any, type:ULTIPA.PropertyType):
	try:
		nullV = nullValue(type)
		return nullV == v
	except Exception as e:
		raise SerializeException(e)
	return False






if __name__ == '__main__':
	print(sys.float_info.max)
	print(sys.int_info)
	print("Int32Null：",Int32Null)
	print("Ret：",0X7FFFFFFF==Int32Null)
	print("Uint32Null：",Uint32Null)
	print("Int64Null：",Int64Null)
	print("Uint64Null：",Uint64Null)
	print("FloatNull：",FloatNull)
	print("DoubleNull：",DoubleNull)
