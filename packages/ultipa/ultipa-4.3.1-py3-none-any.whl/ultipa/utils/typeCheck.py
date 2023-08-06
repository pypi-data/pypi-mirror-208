# -*- coding: utf-8 -*-
import datetime

from ultipa.types import ULTIPA
from ultipa.utils.checkStrTime import is_valid_date


class TypeCheck:

	@staticmethod
	def checkProperty(type, value):
		if type == ULTIPA.PropertyType.PROPERTY_UINT32:
			if isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [uint32],value=%s"

		if type == ULTIPA.PropertyType.PROPERTY_UINT64:
			if isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [uint64],value=%s"

		if type == ULTIPA.PropertyType.PROPERTY_INT32:
			if isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [int32],value=%s"

		if type == ULTIPA.PropertyType.PROPERTY_INT64:
			if isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [int64],value=%s"

		if type in [ULTIPA.PropertyType.PROPERTY_STRING, ULTIPA.PropertyType.PROPERTY_TO,
					ULTIPA.PropertyType.PROPERTY_FROM, ULTIPA.PropertyType.PROPERTY_ID,ULTIPA.PropertyType.PROPERTY_TEXT
					]:
			if isinstance(value, str) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [string],value=%s"

		if type in [ULTIPA.PropertyType.PROPERTY_UUID, ULTIPA.PropertyType.PROPERTY_FROM_UUID, ULTIPA.PropertyType.PROPERTY_TO_UUID]:
			if isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [int64],value=%s"

		if type in [ULTIPA.PropertyType.PROPERTY_FLOAT]:
			if isinstance(value, float) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [float],value=%s"

		if type in [ULTIPA.PropertyType.PROPERTY_DOUBLE]:
			if isinstance(value, float) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [double],value=%s"

		if type == ULTIPA.PropertyType.PROPERTY_DATETIME:
			if is_valid_date(value) != False or isinstance(value, datetime.datetime) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [datetime],value=%s"

		if type == ULTIPA.PropertyType.PROPERTY_TIMESTAMP:
			if is_valid_date(value) != False or isinstance(value, datetime.datetime) or isinstance(value, int) or value is None:
				return True
			else:
				return "%s row [%s] error: failed to serialize value of property %s [timestamp],value=%s"

		return True

if __name__ == '__main__':
	ret = TypeCheck.checkProperty(1,"2019-12-12 15:59:59")
	print(ret)
