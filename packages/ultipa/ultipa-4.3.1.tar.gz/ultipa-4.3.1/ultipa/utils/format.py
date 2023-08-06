import copy
import json
from typing import List

from ultipa.proto.ultipa_pb2 import AttrListData
from ultipa.types.types import ResultType
from ultipa.utils import errors
from ultipa.types import ULTIPA, ULTIPA_RESPONSE, ULTIPA_REQUEST
from ultipa.utils.errors import ParameterException
from ultipa.utils.serialize import _Serialize

#
# class FormatRequest:
#     @staticmethod
#     def easyMakerUqlMaker(command: CommandList, commonParams, commandP: object = None, params: object = None,
#                           IsPassKey: List[str] = None, ):
#         if IsPassKey is None:
#             IsPassKey=[]
#         uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=commonParams)
#         if params:
#             for k in params.__dict__.keys():
#                 if k in IsPassKey:
#                     continue
#                 if params.__dict__[k]:
#                     uqlMaker.addParam(k, params.__dict__[k])
#         return uqlMaker
from ultipa.utils.typeCheck import TypeCheck


class HasDataMap:
	has_ultipa_data: bool
	has_attr_data: bool
	only_attr_list: bool

	def __init__(self, has_ultipa_data, has_attr_data, only_attr_list):
		self.has_ultipa_data = has_ultipa_data
		self.has_attr_data = has_attr_data
		self.only_attr_list = only_attr_list


class FormatResponse:

	@staticmethod
	def resTableToArray(table: ULTIPA.Table):
		# SchemaNameList = ['_nodeSchema', '_edgeSchema']
		tres = []
		headers = []
		if table:
			try:
				for index, header in enumerate(table.headers):
					if not header.property_name:
						if header.property_type == ULTIPA.PropertyType.PROPERTY_NULL:
							header.property_name = f"null({index})"
					headers.append({"property_name": header.property_name,
									"property_type": ULTIPA_REQUEST.Property._getStringByPropertyType(
										header.property_type)})
				tret = ULTIPA.Table(table_name=table.name, headers=headers, table_rows=table.rows)
				tres.append(tret)
			except Exception as e:
				raise errors.ParameterException(e)
		return tret

	@staticmethod
	def formatStatisticsTable(table: ULTIPA.Table):
		headers = []
		if table:
			try:
				for header in table.headers:
					headers.append({"property_name": header.property_name,
									"property_type": ULTIPA_REQUEST.Property._getStringByPropertyType(
										header.property_type)})
				item = {}
				for row in table.rows:
					for index in range(len(row)):
						v = row[index]
						item[table.headers[index].property_name] = int(v)
				tret = ULTIPA.UltipaStatistics(edge_affected=item.get("edge_affected"),
											   node_affected=item.get("node_affected"),
											   total_time_cost=item.get("total_time_cost"),
											   engine_time_cost=item.get("engine_time_cost"))
				return tret
			except Exception as e:
				raise errors.ParameterException(e)


# @staticmethod
# def changeKeyValue(objs, keyForamt: ResponseKeyFormat):
#     if objs and keyForamt:
#         objs_list = []
#         if type(objs) != list:
#             objs_list = [objs]
#         else:
#             objs_list = objs
#         for obj in objs_list:
#             if keyForamt.jsonKeys:
#                 for key in keyForamt.jsonKeys:
#                     if key in obj:
#                         obj[key] = json.loads(obj[key])
#             if keyForamt.boolKeys:
#                 for key in keyForamt.boolKeys:
#                     if key in obj:
#                         obj[key] = obj[key] == "true"
#             if keyForamt.keyReplace:
#                 for key in keyForamt.keyReplace.keys():
#                     if key in obj:
#                         obj[keyForamt.keyReplace[key]] = obj[key]
#                         del obj[key]
#
#             if keyForamt.dataFormat:
#                 for gp in obj:
#                     if gp in keyForamt.dataFormat:
#                         dlist = []
#                         for d in obj.get(gp):
#                             dlist.append({'name': list(d.keys())[0], 'values': list(d.values())[0]})
#                         obj[gp] = dlist
#     return objs


class DataMerge:
	@staticmethod
	def arrayDiff(arr1: "[str]", arr2: "[str]"):
		diff = []
		for i in arr2:
			if i not in arr1:
				diff.append(i)
		return diff

	@staticmethod
	def customizer(objValue, srcValue, key, ignoreKeys):
		if ignoreKeys and key in ignoreKeys:
			return objValue

		if isinstance(objValue, list):
			return objValue + srcValue

	@staticmethod
	def merge(o1: object, o2: object, ignoreKeys: [str] = None):
		if ignoreKeys is None:
			ignoreKeys = []
		retDict = {}
		for key in o1:
			if o1.get(key) and o2.get(key):
				mergeRet = DataMerge.customizer(o1[key], o2[key], key, ignoreKeys)
				retDict.update({key: mergeRet})
			else:
				if isinstance(o1, dict) and isinstance(o1, dict):
					if o1.get(key):
						retDict.update({key: o1.get(key)})
						retDict.update(o2)
		return retDict

	@staticmethod
	def concat(arr1: list, arr2: list, bykey: str = None, ignoreKeys: "[str]" = None):

		if bykey:
			if bykey == 'table_name':
				if isinstance(arr1, list) and isinstance(arr2, list):
					newData = arr1
					newArry = arr2

					# 找出arr1与arr2不同的 table_name
					if isinstance(newData, dict):
						diff = DataMerge.arrayDiff([i[bykey] for i in arr1], [i[bykey] for i in arr2])
					else:
						diff = DataMerge.arrayDiff([y.name for y in newData], [y.name for y in arr2])

					# 如果存在不同的 直接 将table_name 添加到newData
					if diff:
						for di in diff:
							for a2 in arr2:
								if a2.name == di:
									newData.append(ULTIPA.Table(table_name=di, table_rows=a2.rows, headers=a2.headers))

					# 遍历newArry 根据相应table_name 将table添加到 table_rows
					for a2 in newArry:
						for data in newData:
							if a2.name == data.name:
								data.rows += a2.rows
					return newData

			if bykey == 'nodes':
				if isinstance(arr1, list) and isinstance(arr2, list):
					newArry = arr2
					newData = arr1

					arrtList = []

					# 先获取现有存在的alisa
					for new in newData:
						arrtList.append(new.alias)

					# 判断新的arr2中的alias是否存在于arrtlist中
					# 如果没有将arr2添加到newData 返回
					for arr in newArry:
						if arr.alias not in arrtList:
							newData.append(arr)

					# 存在的话直接 根据相应的别名添加到newData
					# 返回 newData
					for arr in newArry:
						if not newData:
							newData.append(arr)
						for new in newData:
							if arr.alias == new.alias:
								new.nodes += arr.nodes
					return newData

			if bykey == 'edges':
				if isinstance(arr1, list) and isinstance(arr2, list):
					newArry = arr2
					newData = arr1

					arrtlist = []
					for new in newData:
						arrtlist.append(new.alias)

					for arr in newArry:
						if arr.alias not in arrtlist:
							newData.append(arr)
							return newData

					for arr in newArry:
						if not newData:
							newData.append(arr)
						for new in newData:
							if arr.alias == new.alias:
								new.edges += arr.edges

					return newData

			if bykey == 'values':
				if isinstance(arr1, list) and isinstance(arr2, list):
					newArry = arr2
					newData = arr1
					arrtlist = []
					for new in newData:
						arrtlist.append(new.alias)

					for arr in newArry:
						if arr.alias not in arrtlist:
							newData.append(arr)
					for arr in newArry:
						if not newData:
							newData.append(arr)
						for new in newData:
							if arr.alias in arrtlist and arr.alias == new.alias:
								new.values += arr.values
					return newData

			if bykey == 'arrays':
				if isinstance(arr1, list) and isinstance(arr2, list):
					newArry = arr2
					newData = arr1
					arrtlist = []
					for new in newData:
						arrtlist.append(new.alias)

					for arr in newArry:
						if arr.alias not in arrtlist:
							newData.append(arr)

					for arr in newArry:
						if not newData:
							newData.append(arr)
						for new in newData:
							if arr.alias in arrtlist and arr.alias == new.alias:
								new.elements += arr.elements
					return newData

		if isinstance(arr1, list) and isinstance(arr2, list):
			arr1.extend(arr2)
			return arr1
		elif isinstance(arr1, dict) and isinstance(arr2, dict):
			return arr1.update(arr2)


class FormatType:

	@staticmethod
	def checkProperty(row, schemaProperties):
		propertyList = []
		rowPropertyList = row.values.keys()
		for property in rowPropertyList:
			findSchema = list(filter(lambda x: x.get('name') == property, schemaProperties))
			if findSchema:
				schemaProperty = findSchema[0]
				reqProperty = ULTIPA_REQUEST.Property(schemaProperty.get("name"))
				reqProperty.setTypeInt(schemaProperty.get("type"))
				propertyList.append(reqProperty)
			else:
				raise ParameterException(
					err=f"row [{row._getIndex()}] error: schema[{row.schema}] doesn't contain property [{property}].")
		return propertyList

	@staticmethod
	def checkNodeRow(i: int, schema: ULTIPA_REQUEST.Schema, row: ULTIPA.EntityRow):
		if row._index != None:
			i = row._index

		if row is None:
			raise ParameterException(err=f"The row [{i}] data is null")

		if row.values is None:
			raise ParameterException(err=f"node row [{i}] error: values are empty but  properties size > 0.")

		if not schema.properties and row.values:
			raise ParameterException(err=f"node row [{i}] error: properties are empty but values size > 0.")

		if len(row.values.keys()) > len(schema.properties):
			raise ParameterException(err=f"node row [{i}] error: values size larger than properties size.")

		if len(row.values.keys()) < len(schema.properties):
			raise ParameterException(err=f"node row [{i}] error: values size smaller than properties size.")

		for proper in schema.properties:
			if proper.isIdType() or proper.isIgnore():
				continue
			if proper.name not in row.values:
				raise ParameterException(
					err=f"node row [{i}] error: values doesn't contain property [{proper.name}].")

	@staticmethod
	def checkEdgeRow(i: int, schema: ULTIPA_REQUEST.Schema, row: ULTIPA.EntityRow):
		if row._index != None:
			i = row._index

		if row is None:
			raise ParameterException(err=f"The row [{i}] data is null")
		if row.values is None:
			raise ParameterException(err=f"edge row [{i}] error: values are empty but properties size > 0.")
		if not schema.properties and row.values:
			raise ParameterException(err=f"edge row [{i}] error: properties are empty but values size > 0.")

		if len(row.values.keys()) > len(schema.properties):
			raise ParameterException(err=f"edge row [{i}] error: values size larger than properties size.")

		if len(row.values.keys()) < len(schema.properties):
			raise ParameterException(err=f"edge row [{i}] error: values size smaller than properties size.")

		if ((row.from_id is None or row.from_id == "") and (row.to_id is None or row.to_id == "")) \
				and (row.from_uuid is None and row.to_uuid is None):
			raise ParameterException(err=f"row [{i}] error: _from/_from_uuid and _to/_to_uuid are null.")

		if (row.from_id != None and row.from_id != "") and (row.to_id is None or row.to_id == ""):
			raise ParameterException(err=f"row [{i}] error: _from has value [{row.from_id}] but _to got null.")

		if (row.from_id is None or row.from_id == "") and (row.to_id != None and row.to_id != ""):
			raise ParameterException(err=f"row [{i}] error: _to has value [{row.to_id}] but _from got null.")

		if row.from_uuid is None and row.to_uuid != None:
			raise ParameterException(
				err=f"row [{i}] error: _to_uuid has value [{row.to_uuid}] but _from_uuid got null.")

		if row.from_uuid != None and row.to_uuid is None:
			raise ParameterException(
				err=f"row [{i}] error: _from_uuid has value [{row.from_uuid}] but _to_uuid got null.")

		for proper in schema.properties:
			if proper.isIdType() or proper.isIgnore():
				continue
			if proper.name not in row.values:
				raise ParameterException(
					err=f"edge row [{i}] error: values doesn't contain property [{proper.name}].")

	@staticmethod
	def checkEntityNodeRow(i: int, schema: ULTIPA_REQUEST.Schema, row: ULTIPA.EntityRow):
		if row._index != None:
			i = row._index

		if row is None:
			raise ParameterException(err=f"The row [{i}] data is null")

		if row.values is None:
			raise ParameterException(err=f"node row [{i}] error: values are empty but  properties size > 0.")

		if not schema.properties and row.values:
			raise ParameterException(err=f"node row [{i}] error: properties are empty but values size > 0.")

		if len(row.values.keys()) > len(schema.properties):
			raise ParameterException(err=f"node row [{i}] error: values size larger than properties size.")

		if len(row.values.keys()) < len(schema.properties):
			raise ParameterException(err=f"node row [{i}] error: values size smaller than properties size.")

		for proper in schema.properties:
			if proper.isIdType() or proper.isIgnore():
				continue
			if proper.name not in row.values:
				raise ParameterException(
					err=f"node row [{i}] error: values doesn't contain property [{proper.name}].")

	@staticmethod
	def checkEntityEdgeRow(i: int, schema: ULTIPA_REQUEST.Schema, row: ULTIPA.EntityRow):
		if row._index != None:
			i = row._index

		if row is None:
			raise ParameterException(err=f"The row [{i}] data is null")
		if row.values is None:
			raise ParameterException(err=f"edge row [{i}] error: values are empty but properties size > 0.")
		if not schema.properties and row.values:
			raise ParameterException(err=f"edge row [{i}] error: properties are empty but values size > 0.")

		if len(row.values.keys()) > len(schema.properties):
			raise ParameterException(err=f"edge row [{i}] error: values size larger than properties size.")

		if len(row.values.keys()) < len(schema.properties):
			raise ParameterException(err=f"edge row [{i}] error: values size smaller than properties size.")

		if ((row.from_id is None or row.from_id == "") and (row.to_id is None or row.to_id == "")) \
				and (row.from_uuid is None and row.to_uuid is None):
			raise ParameterException(err=f"row [{i}] error: _from/_from_uuid and _to/_to_uuid are null.")

		if (row.from_id != None and row.from_id != "") and (row.to_id is None or row.to_id == ""):
			raise ParameterException(err=f"row [{i}] error: _from has value [{row.from_id}] but _to got null.")

		if (row.from_id is None or row.from_id == "") and (row.to_id != None and row.to_id != ""):
			raise ParameterException(err=f"row [{i}] error: _to has value [{row.to_id}] but _from got null.")

		if row.from_uuid is None and row.to_uuid != None:
			raise ParameterException(
				err=f"row [{i}] error: _to_uuid has value [{row.to_uuid}] but _from_uuid got null.")

		if row.from_uuid != None and row.to_uuid is None:
			raise ParameterException(
				err=f"row [{i}] error: _from_uuid has value [{row.from_uuid}] but _to_uuid got null.")

		for proper in schema.properties:
			if proper.isIdType() or proper.isIgnore():
				continue
			if proper.name not in row.values:
				raise ParameterException(
					err=f"edge row [{i}] error: values doesn't contain property [{proper.name}].")

	@staticmethod
	def status(_status, host: str = None) -> ULTIPA.Status:
		statusData = ULTIPA.Status(code=_status.error_code, message=_status.msg)
		isNotRaftMode = _status.error_code == ULTIPA.Code.NOT_RAFT_MODE

		if _status.cluster_info or isNotRaftMode:
			leaderPeer = None
			_followrs = []
			if _status.cluster_info.leader_address or host:
				leaderPeer = ULTIPA.RaftPeerInfo(_status.cluster_info.leader_address or host, True, True, False, False,
												 False)
				leaderPeer.isAlgoExecutable = isNotRaftMode or False
				_followrs.append(leaderPeer)
			for foll in _status.cluster_info.followers:
				status = foll.status == 1
				peer = ULTIPA.RaftPeerInfo(foll.address)
				peer.status = status
				peer.isLeader = False
				peer.isAlgoExecutable = False
				peer.isFollowerReadable = False
				if status:
					peer.isAlgoExecutable = foll.role & ULTIPA.FollowerRole.ROLE_ALGO_EXECUTABLE and True or False
					peer.isFollowerReadable = foll.role & ULTIPA.FollowerRole.ROLE_READABLE and True or False
				peer.isUnset = foll.role == ULTIPA.FollowerRole.ROLE_UNSET
				_followrs.append(peer)
			clusterInfo = ULTIPA.ClusterInfo(_status.cluster_info.redirect, _followrs, leader=leaderPeer)
			statusData.clusterInfo = clusterInfo
		return statusData

	@staticmethod
	def getRaftStatus(data: dict) -> ULTIPA.Status:
		statusData = ULTIPA.Status(code=data.get("code"), message=data.get("message"))
		clusterInfo = ULTIPA.ClusterInfo(redirect=data.get("redirectHost"), raftPeers=data.get("followersPeerInfos"),
										 leader=data.get("leaderInfos"))
		statusData.clusterInfo = clusterInfo
		return statusData

	@staticmethod
	def table(_table, timeZone, timeZoneOffset) -> ULTIPA.Table:
		table_name = _table.table_name
		headers = []
		for h in _table.headers:
			headers.append(h)
		values = []
		for index, row in enumerate(_table.table_rows):
			_vs = []
			for index2, _v in enumerate(row.values):
				if len(headers) > 0:
					property_type = headers[index2].property_type
				else:
					property_type = ULTIPA.PropertyType.PROPERTY_STRING
				# header type is NULL
				# if property_type == ULTIPA.PropertyType.PROPERTY_NULL:
				# 	_vs.append(None)
				# 	continue
				_seria = _Serialize(type=property_type, value=_v, timeZone=timeZone, timeZoneOffset=timeZoneOffset)
				unret = _seria.unserialize()
				_vs.append(unret)
			values.append(_vs)
		tableData = ULTIPA.Table(table_name=table_name, headers=headers, table_rows=values)
		return tableData

	@staticmethod
	def tables(_tables, timeZone, timeZoneOffset) -> List[ULTIPA.Table]:
		tablesData = []
		if _tables:
			for table in _tables:
				tableData = FormatType.table(table, timeZone, timeZoneOffset)
				# for ta in tables:
				tret = FormatResponse.resTableToArray(table=tableData)
				# tablesData += tret
				tablesData.append(tret)
		return tablesData

	@staticmethod
	def statistics(_table, timeZone, timeZoneOffset) -> ULTIPA.UltipaStatistics:
		if not _table:
			return None
		tableData = FormatType.table(_table, timeZone, timeZoneOffset)
		tret = FormatResponse.formatStatisticsTable(table=tableData)
		return tret

	@staticmethod
	def nodeTable(nodeTableData, timeZone, timeZoneOffset):
		SchemaTypeDict = {}
		SchemaHeaderDict = {}
		SchemaSubTypeHeaderDict = {}
		tables = []
		for header in nodeTableData.node_table.schemas:
			schemaName = header.schema_name
			typesDict = {}
			headerDict = {}
			subTypesDict = {}
			for index, header in enumerate(header.properties):
				typesDict.update({index: header.property_type})
				headerDict.update({index: header.property_name})
				subTypesDict.update({index: header.sub_types})

			SchemaTypeDict.update({schemaName: typesDict})
			SchemaHeaderDict.update({schemaName: headerDict})
			SchemaSubTypeHeaderDict.update({schemaName: subTypesDict})

		schemaTypeGet = SchemaTypeDict.get
		schemaHeaderGet = SchemaHeaderDict.get
		schemaSubTypeGet = SchemaSubTypeHeaderDict.get

		for node_row in nodeTableData.node_table.entity_rows:
			if node_row.is_null is True:
				tables.append(ULTIPA.Node(id=None, values=None, schema_name=None, uuid=None))
				continue
			data = {}
			_id = node_row.id
			uuid = node_row.uuid

			schema_name = node_row.schema_name
			if node_row.values:
				for index, uvalue in enumerate(node_row.values):
					seria = _Serialize(type=schemaTypeGet(schema_name).get(index), value=uvalue,
									   subTypes=schemaSubTypeGet(schema_name).get(index), timeZone=timeZone,
									   timeZoneOffset=timeZoneOffset)
					value = seria.unserialize()
					data.update({schemaHeaderGet(schema_name).get(index): value})
			node = ULTIPA.Node(id=_id, values=data, schema_name=schema_name, uuid=uuid)
			tables.append(node)
		return tables

	@staticmethod
	def edgeTable(edgeTableData, timeZone, timeZoneOffset):
		SchemaTypeDict = {}
		SchemaHeaderDict = {}
		SchemaSubTypeHeaderDict = {}
		tables = []
		for header in edgeTableData.edge_table.schemas:
			schemaName = header.schema_name
			typesDict = {}
			headerDict = {}
			subTypesDict = {}
			for index, header in enumerate(header.properties):
				typesDict.update({index: header.property_type})
				headerDict.update({index: header.property_name})
				subTypesDict.update({index: header.sub_types})

			SchemaTypeDict.update({schemaName: typesDict})
			SchemaHeaderDict.update({schemaName: headerDict})
			SchemaSubTypeHeaderDict.update({schemaName: subTypesDict})

		schemaTypeGet = SchemaTypeDict.get
		schemaHeaderGet = SchemaHeaderDict.get
		schemaSubTypeGet = SchemaSubTypeHeaderDict.get

		for edge_row in edgeTableData.edge_table.entity_rows:
			if edge_row.is_null is True:
				tables.append(ULTIPA.Edge(from_id=None, to_id=None, values=None, uuid=None, from_uuid=None,
										  to_uuid=None, schema_name=None))
				continue
			data = {}
			_from_uuid = edge_row.from_uuid
			_from_id = edge_row.from_id
			_to_uuid = edge_row.to_uuid
			_to_id = edge_row.to_id
			schema_name = edge_row.schema_name
			uuid = edge_row.uuid
			if edge_row.values:
				for index, uvalue in enumerate(edge_row.values):
					seria = _Serialize(type=schemaTypeGet(schema_name).get(index), value=uvalue,
									   subTypes=schemaSubTypeGet(schema_name).get(index), timeZone=timeZone,
									   timeZoneOffset=timeZoneOffset)
					value = seria.unserialize()
					data.update({schemaHeaderGet(schema_name).get(index): value})
			edge = ULTIPA.Edge(from_id=_from_id, to_id=_to_id, values=data, uuid=uuid, from_uuid=_from_uuid,
							   to_uuid=_to_uuid, schema_name=schema_name)
			tables.append(edge)
		return tables

	@staticmethod
	def attrEntity(entityRows, type: str):
		entityList = []
		for data in entityRows.entity_rows:
			if type == "node":
				entityList.append(ULTIPA.Node(values=None, uuid=data.uuid))
			else:
				entityList.append(ULTIPA.Edge(values=None, uuid=data.uuid))
		return entityList

	@staticmethod
	def propertyType(type: str) -> ULTIPA.PropertyType:
		'''
		将用户传入的type 转化为 ULTIPA.PropertyType
		:param type:
		:return:
		'''
		if type.upper() == 'PROPERTY_STRING' or type.upper() == 'STRING':
			type = ULTIPA.PropertyType.PROPERTY_STRING
		elif type.upper() == 'PROPERTY_INT32' or type.upper() == 'INT32':
			type = ULTIPA.PropertyType.PROPERTY_INT32
		elif type.upper() == 'PROPERTY_INT64' or type.upper() == 'INT64':
			type = ULTIPA.PropertyType.PROPERTY_INT64
		elif type.upper() == 'PROPERTY_FLOAT' or type.upper() == 'FLOAT':
			type = ULTIPA.PropertyType.PROPERTY_FLOAT
		elif type.upper() == 'PROPERTY_DOUBLE' or type.upper() == 'DOUBLE':
			type = ULTIPA.PropertyType.PROPERTY_DOUBLE
		elif type.upper() == 'PROPERTY_UINT32' or type.upper() == 'UINT32':
			type = ULTIPA.PropertyType.PROPERTY_UINT32
		elif type.upper() == 'PROPERTY_UINT64' or type.upper() == 'UINT64':
			type = ULTIPA.PropertyType.PROPERTY_UINT64
		elif type.upper() == 'PROPERTY_DATETIME' or type.upper() == 'DATETIME':
			type = ULTIPA.PropertyType.PROPERTY_DATETIME
		elif type.upper() == 'PROPERTY_TIMESTAMP' or type.upper() == 'TIMESTAMP':
			type = ULTIPA.PropertyType.PROPERTY_TIMESTAMP
		elif type.upper() == 'PROPERTY_TEXT' or type.upper() == 'TEXT':
			type = ULTIPA.PropertyType.PROPERTY_TEXT
		elif type.upper() == 'PROPERTY_UUID' or type.upper() == 'UUID':
			type = ULTIPA.PropertyType.PROPERTY_UUID
		elif type.upper() == 'PROPERTY_ID' or type.upper() == 'ID':
			type = ULTIPA.PropertyType.PROPERTY_ID
		elif type.upper() == 'PROPERTY_FROM' or type.upper() == 'FROM':
			type = ULTIPA.PropertyType.PROPERTY_FROM
		elif type.upper() == 'PROPERTY_FROM_UUID' or type.upper() == 'FROM_UUID':
			type = ULTIPA.PropertyType.PROPERTY_FROM_UUID
		elif type.upper() == 'PROPERTY_TO' or type.upper() == 'TO':
			type = ULTIPA.PropertyType.PROPERTY_TO
		elif type.upper() == 'PROPERTY_TO_UUID' or type.upper() == 'TO_UUID':
			type = ULTIPA.PropertyType.PROPERTY_TO_UUID
		elif type.upper() == 'PROPERTY_IGNORE' or type.upper() == 'IGNORE':
			type = ULTIPA.PropertyType.PROPERTY_IGNORE

		return type

	@staticmethod
	def _formatTableHeader(headers):
		headerList = []
		headertype = {}
		if isinstance(headers, str):
			headers = json.loads(headers)
		if isinstance(headers, list) and isinstance(headers, list):
			for index, header in enumerate(headers):
				headdic = {}
				if isinstance(header, dict):
					type = FormatType.propertyType(header.get('type'))
					headdic.update({'property_name': header.get('name')})
					headdic.update({'property_type': type})
					# headertype.update({index: {header.get('name'): type}})
					headertype.update({header.get('name'): type})
					headerList.append(headdic)
				else:
					headdic.update({'property_name': header.name})
					headdic.update({'property_type': header.type})
					# headertype.update({index: {header.name: header.type}})
					if header.name in headertype:
						headertype.update({header.name: header.type})
						headerList.append(headdic)
					else:
						raise ParameterException('Attribute names cannot be the same')
		else:
			raise ParameterException(err='The headers and rows must be list')

		return (headerList, headertype)

	@staticmethod
	def pathScheams(path):
		nodeSchemas = {}
		edgeSchemas = {}
		for header in path.node_table.schemas:
			schemaName = header.schema_name
			propetyList = []
			for index, property in enumerate(header.properties):
				newproperty = ULTIPA.SchemaProperty()
				newproperty.name = property.property_name
				newproperty.type = ULTIPA_REQUEST.Property._getStringByPropertyType(property.property_type)
				propetyList.append(newproperty)
			nodeSchemas.update({schemaName: ULTIPA.Schema(None, schemaName, propetyList, None, None)})
		for header in path.edge_table.schemas:
			schemaName = header.schema_name
			propetyList = []
			for index, property in enumerate(header.properties):
				newproperty = ULTIPA.SchemaProperty()
				newproperty.name = property.property_name
				newproperty.type = ULTIPA_REQUEST.Property._getStringByPropertyType(property.property_type)
				propetyList.append(newproperty)
			edgeSchemas.update({schemaName: ULTIPA.Schema(None, schemaName, propetyList, None, None)})
		return nodeSchemas, edgeSchemas

	# @staticmethod
	# def formatTableHeader(rows: Dict, propertyList: List):
	#     '''
	#     :param rows: 传进的rows
	#     :param property: 查询数据库获取的属性
	#     :return:
	#     '''
	#     headerList = []
	#     if len(propertyList) > 0:
	#         if not rows:
	#             return headerList
	#         for key in rows[0].keys():
	#             if key not in ['_id', '_from_id', '_to_id', '_o', '_from_o', '_to_o']:
	#                 find = list(filter(lambda x: x.get('name') == key, propertyList))
	#                 if find:
	#                     headerList.append({"name": key, "type": find[0].get('type')})
	#                 else:
	#                     raise ParameterException(err=f'The database does not have a {key} property!')
	#     else:
	#         raise ParameterException(err='The database has no properties!')
	#     return headerList

	@staticmethod
	def toNodeTableSingle(headers: List[dict], schemaName: str, rows: list, timeZoneOffset=None) -> ULTIPA.NodeTable:
		newHeaderList = []
		# 根据 rows 生成新的headers List

		schema_name = schemaName
		find = list(filter(lambda x: x.get('name') == schema_name, headers))
		if find:
			newproperties = []
			newkeys = []
			headerList, _headertype = FormatType._formatTableHeader(find[0].get('properties'))
			for allkeys in rows:
				for key in allkeys.keys():
					if key not in newkeys:
						newkeys.append(key)

			for checkKey in rows:
				k = list(checkKey.keys())
				if k != newkeys:
					raise ParameterException(f'properties of all nodes should be consistent')

			for nkey in newkeys:
				if nkey in ['_uuid', '_id', '_from_uuid', '_to_uuid', '_from_id', '_to_id']:
					continue
				findp = list(filter(lambda x: x.get('property_name') == nkey, headerList))
				if findp:
					newproperties.append(findp[0])
				else:
					raise ParameterException(f'{nkey} property not exit')

			newHeaderList.append({"schema_name": schema_name, "properties": newproperties})
		else:
			raise ParameterException(f'{schema_name} schema not exit')

		nodetable = ULTIPA.NodeTable(schemas=newHeaderList, nodeRows=[])
		# 给nodetable.nodeRowsList 添加数据

		for row in rows:
			nodedata = {}
			values = []
			for data in row.keys():
				if data in ['_id', '_uuid']:
					if data == '_uuid':
						if row.get(data) < 0:
							raise ParameterException('Error the _uuid must be greater than 0')
					nodedata.update({data[1:]: row.get(data)})
					continue
			for headerT in nodetable.schemas:
				for headerPropertyName in headerT.get('properties'):
					if schema_name == headerT.get("schema_name"):
						for rdata in row.keys():
							if rdata in ['_uuid', '_id', '_from_uuid', '_to_uuid', '_from_id', '_to_id']:
								continue
							# findproperty = list(
							#     filter(lambda x: x.get('property_name') == rdata, headerT.get("properties")))
							if headerPropertyName.get('property_name') == rdata:
								type = headerPropertyName.get('property_type')
								if type != None:
									_seria = _Serialize(type=type, value=row.get(rdata), name=rdata,
														timeZoneOffset=timeZoneOffset)
									sdata = _seria.serialize()
									values.append(sdata)
									continue
								else:
									raise ParameterException('Please create Node Property')
			nodedata.update({'schema_name': schema_name, 'values': values})
			nodetable.nodeRows.append(nodedata)
		return nodetable

	@staticmethod
	def serializeNodeTable(nodeTable: ULTIPA_REQUEST.InsertNodeTable) -> ULTIPA.NodeTable:

		newNodeTable = ULTIPA.NodeTable([], [])
		for schema in nodeTable.schemas:
			properties = []
			for prop in schema.properties:
				if prop.isIdType() or prop.isIgnore():
					continue
				properties.append({"property_name": prop.name, "property_type": prop.type})
			newNodeTable.schemas.append({"schema_name": schema.name, "properties": properties})

		for i, row in enumerate(nodeTable.nodeRows):
			schemaName = row.schema
			if schemaName is None:
				raise ParameterException(err=f"The schema_name [{i}] data is null")
			findSchemaType = list(filter(lambda x: x.name == schemaName, nodeTable.schemas))
			if findSchemaType:
				properties = findSchemaType[0].properties
				values = []
				if row is None:
					raise ParameterException(err=f"The row [{i}] data is null")

				if row.values is None:
					raise ParameterException(err=f"node row [{i}] error: values are empty but  properties size > 0.")

				if not properties and row.values:
					raise ParameterException(err=f"node row [{i}] error: properties are empty but values size > 0.")

				if len(row.values.keys()) > len(properties):
					raise ParameterException(err=f"node row [{i}] error: node values size larger than properties size.")

				if len(row.values.keys()) < len(properties):
					raise ParameterException(err=f"node row [{i}] error: values size smaller than properties size")

				for proper in properties:
					# if proper.isIdType() or proper.isIgnore():
					#     continue
					if proper.name in row.values:
						try:
							value = row.values.get(proper.name)
							ptype = proper.type
							_seria = _Serialize(type=ptype, value=value)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							raise ParameterException(err=f"node row [{i}] error:{e}")
					else:
						raise ParameterException(
							err=f"node row [{i}] error: values doesn't contain property [{proper.name}]")
				data = {"schema_name": schemaName, "values": values}
				if row.uuid:
					data.update({"uuid": row.uuid})
				if row.id:
					data.update({"id": row.id})

				newNodeTable.nodeRows.append(data)

			else:
				raise ParameterException(err=f"The schema [{schemaName}] is not exit")
		return newNodeTable

	@staticmethod
	def serializeEdgeTable(edgeTable: ULTIPA_REQUEST.InsertEdgeTable) -> ULTIPA.EdgeTable:
		newEdgeTable = ULTIPA.EdgeTable([], [])
		for schema in edgeTable.schemas:
			properties = []
			for prop in schema.properties:
				if prop.isIdType() or prop.isIgnore():
					continue
				properties.append({"property_name": prop.name, "property_type": prop.type})
			newEdgeTable.schemas.append({"schema_name": schema.name, "properties": properties})
		for i, row in enumerate(edgeTable.edgeRows):
			schemaName = row.schema
			if schemaName is None:
				raise ParameterException(err=f"The schema_name [{i}] data is null")
			findSchemaType = list(filter(lambda x: x.name == schemaName, edgeTable.schemas))
			if findSchemaType:
				properties = findSchemaType[0].properties
				values = []
				if row is None:
					raise ParameterException(err=f"The row [{i}] data is null")
				if row.values is None:
					raise ParameterException(err=f"edge row [{i}] error: values are empty but properties size >0.")
				if not properties and row.values:
					raise ParameterException(err=f"edge row [{i}] error: properties are empty but values size >0.")

				if len(row.values.keys()) > len(properties):
					raise ParameterException(err=f"edge row [{i}] error: values size larger than properties size.")

				if len(row.values.keys()) < len(properties):
					raise ParameterException(err=f"edge row [{i}] error: values size smaller than properties size")

				if ((row.from_id is None and row.from_id == "") and (row.to_id is None and row.to_id == "")) \
						and (row.from_uuid is None and row.to_uuid is None):
					raise ParameterException(err=f"row [{i}] error: _from/_from_uuid and _to/_to_uuid are null.")

				if (row.from_id != None and row.from_id != "") and (row.to_id is None and row.to_id == ""):
					raise ParameterException(err=f"row [{i}] error: _from has value [{row.from_id}] but _to got null")

				if (row.from_id is None and row.from_id == "") and (row.to_id != None and row.to_id != ""):
					raise ParameterException(err=f"row [{i}] error: _to has value [{row.to_id}] but _from got null")

				if row.from_uuid is None and row.to_uuid != None:
					raise ParameterException(
						err=f"row [{i}] error: _to_uuid has value [{row.to_uuid}] but _from_uuid got null")

				if row.from_uuid != None and row.to_uuid is None:
					raise ParameterException(
						err=f"row [{i}] error: _from_uuid has value [{row.from_uuid}] but _to_uuid got null")

				for proper in properties:
					if proper.isIdType() or proper.isIgnore():
						continue
					if proper.name in row.values:
						try:
							value = row.values.get(proper.name)
							ptype = proper.type
							_seria = _Serialize(type=ptype, value=value)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							raise ParameterException(err=f"node row [{i}] error:{e}")
					else:
						raise ParameterException(
							err=f"edge row [{i}] error: values doesn't contain property [{proper.name}]")
				data = {"schema_name": schemaName, "values": values}
				if row.from_uuid:
					data.update({"from_uuid": row.from_uuid})
				if row.to_uuid:
					data.update({"to_uuid": row.to_uuid})
				if row.from_id:
					data.update({"from_id": row.from_id})
				if row.to_id:
					data.update({"to_id": row.to_id})
				newEdgeTable.edgeRows.append(data)
		return newEdgeTable

	@staticmethod
	def makeNodeTable(schema: ULTIPA_REQUEST.Schema, rows: List[ULTIPA.Node], timeZoneOffset=None) -> ULTIPA.NodeTable:

		nodetable = ULTIPA.NodeTable([], [])
		nodetable.schemas.append({"schema_name": schema.name, "properties": []})

		for prop in schema.properties:
			if prop.isIdType() or prop.isIgnore():
				continue
			nodetable.schemas[0].get("properties").append({"property_name": prop.name, "property_type": prop.type})
		for i, row in enumerate(rows):
			append = True
			values = []
			FormatType.checkNodeRow(i, schema, row)
			for proper in schema.properties:
				if proper.isIdType() or proper.isIgnore():
					continue
				if proper.name in row.values:
					value = row.values.get(proper.name)
					ptype = proper.type
					checkRet = TypeCheck.checkProperty(ptype, value)
					if isinstance(checkRet, bool):
						try:
							_seria = _Serialize(type=ptype, value=value, name=proper.name,
												timeZoneOffset=timeZoneOffset)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							if len(e.args) > 0 and "%s" in e.args[0]:
								e = e.args[0] % (proper.name, value)
							raise ParameterException(err=f"node row [{i}] error: {e}")

					else:
						raise ParameterException(
							err=checkRet % ("node", i, proper.name, value))
				else:
					raise ParameterException(
						err=f"node row [{i}] error: values doesn't contain property [{proper.name}].")
			# if config.insert_type == ULTIPA.InsertType.UPSERT:
			#     errorItem.update({i: ULTIPA.InsertErrorCodeMsgMap.E10006})
			#     append = False
			#     break
			# else:
			#     ptype = proper.type
			#     _seria = _Serialize(type=ptype, value=None)
			#     _seria.setDefaultValue()
			#     sdata = _seria.serialize()
			#     values.append(sdata)
			if append:
				data = {"schema_name": schema.name, "values": values}
				if row.uuid:
					data.update({"uuid": row.uuid})
				if row.id:
					data.update({"id": row.id})

				nodetable.nodeRows.append(data)
		return nodetable

	@staticmethod
	def makeEntityNodeTable(schema: ULTIPA_REQUEST.Schema, entity_rows: List[ULTIPA.EntityRow],
							timeZoneOffset=None) -> ULTIPA.NodeEntityTable:

		nodetable = ULTIPA.NodeEntityTable([], [])
		nodetable.schemas.append({"schema_name": schema.name, "properties": []})

		for prop in schema.properties:
			if prop.isIdType() or prop.isIgnore():
				continue
			nodetable.schemas[0].get("properties").append(
				{"property_name": prop.name, "property_type": prop.type, "sub_types": prop.subTypes})
		for i, row in enumerate(entity_rows):
			append = True
			values = []
			FormatType.checkEntityNodeRow(i, schema, row)
			for proper in schema.properties:
				if proper.isIdType() or proper.isIgnore():
					continue
				if proper.name in row.values:
					value = row.values.get(proper.name)
					ptype = proper.type
					checkRet = TypeCheck.checkProperty(ptype, value)
					if isinstance(checkRet, bool):
						try:
							_seria = _Serialize(type=ptype, value=value, name=proper.name,
												timeZoneOffset=timeZoneOffset, subTypes=proper.subTypes)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							if len(e.args) > 0 and "%s" in e.args[0]:
								e = e.args[0] % (proper.name, value)
							raise ParameterException(err=f"node row [{row._getIndex()}] error: {e}")

					else:
						raise ParameterException(
							err=checkRet % ("node", row._getIndex(), proper.name, value))
				else:
					raise ParameterException(
						err=f"node row [{row._getIndex()}] error: values doesn't contain property [{proper.name}].")
			if append:
				data = {"schema_name": schema.name, "values": values}
				if row.uuid:
					data.update({"uuid": row.uuid})
				if row.id:
					data.update({"id": row.id})

				nodetable.nodeRows.append(data)
		return nodetable

	@staticmethod
	def makeEdgeTable(schema: ULTIPA_REQUEST.Schema, rows: List[ULTIPA.Edge], timeZoneOffset=None) -> ULTIPA.EdgeTable:
		edgetable = ULTIPA.EdgeTable([], [])
		edgetable.schemas.append({"schema_name": schema.name, "properties": []})
		for prop in schema.properties:
			if prop.isIdType() or prop.isIgnore():
				continue
			edgetable.schemas[0].get("properties").append({"property_name": prop.name, "property_type": prop.type})
		for i, row in enumerate(rows):
			append = True
			values = []
			FormatType.checkEdgeRow(i, schema, row)
			for proper in schema.properties:
				if proper.isIdType() or proper.isIgnore():
					continue
				if proper.name in row.values:
					value = row.values.get(proper.name)
					ptype = proper.type
					checkRet = TypeCheck.checkProperty(ptype, value)
					if isinstance(checkRet, bool):
						try:
							_seria = _Serialize(type=ptype, value=value, name=proper.name,
												timeZoneOffset=timeZoneOffset)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							raise ParameterException(err=f"edge row [{i}] error:{e}.")
					else:
						raise ParameterException(
							err=checkRet % ("edge", i, proper.name, value))
				else:
					raise ParameterException(
						err=f"edge row [{i}] error: values doesn't contain property [{proper.name}].")

			if append:
				data = {"schema_name": schema.name, "values": values}
				if row.from_uuid:
					data.update({"from_uuid": row.from_uuid})
				if row.to_uuid:
					data.update({"to_uuid": row.to_uuid})
				if row.from_id:
					data.update({"from_id": row.from_id})
				if row.to_id:
					data.update({"to_id": row.to_id})
				if row.uuid:
					data.update({"uuid": row.uuid})
				edgetable.edgeRows.append(data)
		return edgetable

	@staticmethod
	def makeEntityEdgeTable(schema: ULTIPA_REQUEST.Schema, rows: List[ULTIPA.EntityRow],
							timeZoneOffset=None) -> ULTIPA.EdgeEntityTable:
		edgetable = ULTIPA.EdgeTable([], [])
		edgetable.schemas.append({"schema_name": schema.name, "properties": []})
		for prop in schema.properties:
			if prop.isIdType() or prop.isIgnore():
				continue
			edgetable.schemas[0].get("properties").append({"property_name": prop.name, "property_type": prop.type})
		for i, row in enumerate(rows):
			append = True
			values = []
			FormatType.checkEntityEdgeRow(i, schema, row)
			for proper in schema.properties:
				if proper.isIdType() or proper.isIgnore():
					continue
				if proper.name in row.values:
					value = row.values.get(proper.name)
					ptype = proper.type
					checkRet = TypeCheck.checkProperty(ptype, value)
					if isinstance(checkRet, bool):
						try:
							_seria = _Serialize(type=ptype, value=value, name=proper.name, subTypes=proper.subTypes,
												timeZoneOffset=timeZoneOffset)
							sdata = _seria.serialize()
							values.append(sdata)
						except Exception as e:
							raise ParameterException(err=f"edge row [{row._getIndex()}] error:{e}.")
					else:
						raise ParameterException(
							err=checkRet % ("edge", row._getIndex(), proper.name, value))
				else:
					raise ParameterException(
						err=f"edge row [{row._getIndex()}] error: values doesn't contain property [{proper.name}].")

			if append:
				data = {"schema_name": schema.name, "values": values}
				if row.from_uuid:
					data.update({"from_uuid": row.from_uuid})
				if row.to_uuid:
					data.update({"to_uuid": row.to_uuid})
				if row.from_id:
					data.update({"from_id": row.from_id})
				if row.to_id:
					data.update({"to_id": row.to_id})
				if row.uuid:
					data.update({"uuid": row.uuid})
				edgetable.edgeRows.append(data)
		return edgetable

	@staticmethod
	def toEdgeTableSingle(headers: List[object], schemaName: str, values: list,
						  timeZoneOffset=None) -> ULTIPA.EdgeTable:
		# headerList, headertype = FormatType._formatTableHeader(headers)
		# edgetable = ULTIPA.EdgeTable(headersList=headerList, edgeRowsList=[])
		# edgetable.headersList = headerList
		newHeaderList = []
		schema_name = schemaName
		find = list(filter(lambda x: x.get('name') == schema_name, headers))
		if find:
			newproperties = []
			newkeys = []
			headerList, _headertype = FormatType._formatTableHeader(find[0].get('properties'))

			for allkeys in values:
				for key in allkeys.keys():
					if key not in newkeys:
						newkeys.append(key)
			for checkKey in values:
				k = list(checkKey.keys())
				if k != newkeys:
					raise ParameterException(f'properties of all edges should be consistent')

			for nkey in newkeys:
				if nkey in ['_uuid', '_id', '_from_uuid', '_to_uuid', '_from', '_to']:
					continue
				findp = list(filter(lambda x: x.get('property_name') == nkey, headerList))
				if findp:
					newproperties.append(findp[0])
				else:
					raise ParameterException(f'{nkey} property not exit')

			newHeaderList.append({"schema_name": schema_name, "properties": newproperties})
		else:
			raise ParameterException(f'{schema_name} schema not exit')

		edgetable = ULTIPA.EdgeTable(schemas=newHeaderList, edgeRows=[])

		for row in values:
			edgedata = {}
			values = []
			for data in row.keys():
				# '_from_o','_to_o' 为 string
				if data in ['_uuid', '_id', '_from_uuid', '_to_uuid', '_from', '_to']:
					if data in ['_uuid', '_from_uuid', '_to_uuid']:
						if row.get(data) < 0:
							raise ParameterException('Error the _uuid,_from_uuid,_to_uuid must be greater than 0')
					if data == '_from':
						edgedata.update({'from_id': row.get(data)})
						continue
					if data == '_to':
						edgedata.update({'to_id': row.get(data)})
						continue
					edgedata.update({data[1:]: row.get(data)})
					continue

			if not edgedata:
				raise ParameterException()

			for headerT in edgetable.schemas:
				for headerPropertyName in headerT.get('properties'):
					if schema_name == headerT.get("schema_name"):
						for rdata in row.keys():
							if rdata in ['_uuid', '_id', '_from_uuid', '_to_uuid', '_from', '_to']:
								continue
							if headerPropertyName.get('property_name') == rdata:
								type = headerPropertyName.get('property_type')
								if type != None:
									_seria = _Serialize(type=type, value=row.get(rdata), name=rdata,
														timeZoneOffset=timeZoneOffset)
									sdata = _seria.serialize()
									values.append(sdata)
									continue
								else:
									raise ParameterException('Please create Node Property')

			edgedata.update({'schema_name': schema_name, 'values': values})
			edgetable.edgeRows.append(edgedata)
		return edgetable

	@staticmethod
	def nodeAliases(_nodes, timeZone, timeZoneOffset) -> List[ULTIPA.NodeAlias]:
		nodeAliasesData = []
		if _nodes:
			for node in _nodes:
				nodesData = FormatType.nodeTable(node, timeZone, timeZoneOffset)
				nodeAliasData = ULTIPA.NodeAlias(alias=node.alias, nodes=nodesData)
				# nodeAliasData = DataItem(alias=node.alias,data=nodesData,type=ResultType.RESULT_TYPE_NODE)
				# nodeAliasesData.append({'alias':node.alias,node.alias:nodesData})
				nodeAliasesData.append(nodeAliasData)
		# nodeAliasesData = nodeAliasData
		return nodeAliasesData

	@staticmethod
	def attrNodeEntityTable(data) -> List[ULTIPA.Node]:
		return FormatType.attrEntity(data, "node")

	@staticmethod
	def attrEdgeEntityTable(data) -> List[ULTIPA.Edge]:
		return FormatType.attrEntity(data, "edge")

	@staticmethod
	def nodeAliases1(_nodes) -> List[ULTIPA.NodeAlias]:
		if not _nodes:
			return []
		nodeData = [None] * len(_nodes)
		index = -1
		for node in _nodes:
			index += 1
			nodesData = FormatType.nodeTable(node)
			nodeAliasData = ULTIPA.NodeAlias(alias=node.alias, nodes=nodesData)
			# nodeAliasData = DataItem(alias=node.alias,data=nodesData,type=ResultType.RESULT_TYPE_NODE)
			# nodeAliasesData.append({'alias':node.alias,node.alias:nodesData})
			nodeData[index] = nodeAliasData
		# nodeAliasesData = nodeAliasData
		return nodeData

	@staticmethod
	def edgeAliases(_edges, timeZone, timeZoneOffset) -> List[ULTIPA.EdgeAlias]:
		edgeAliasesData = []
		if _edges:
			for edge in _edges:
				edgesData = FormatType.edgeTable(edge, timeZone, timeZoneOffset)
				edgeAliasData = ULTIPA.EdgeAlias(alias=edge.alias, edges=edgesData)
				edgeAliasesData.append(edgeAliasData)
		return edgeAliasesData

	@staticmethod
	def values(_values) -> 'dict':
		value_dict = {}
		if _values:
			for value in _values:
				value_dict.update({value.key: value.value})
		return value_dict

	@classmethod
	def parseAttrListData(cls, datas) -> List[ULTIPA.PaserAttrListData]:
		PaserAttrRetList = []
		for data in datas:
			attrListRet = []
			pathListRet = []
			nodetRet = None
			edgeRet = None
			attrListData = AttrListData()
			attrListData.ParseFromString(data)
			if attrListData.type == ULTIPA.ResultType.RESULT_TYPE_ATTR:
				for attr in attrListData.attrs:
					attrListRet.append(cls.parseAttr(attr, None))

			if attrListData.type == ULTIPA.ResultType.RESULT_TYPE_PATH:
				pathListRet.extend(FormatType.attrPath(attrListData.paths, None, None))

			if attrListData.type == ULTIPA.ResultType.RESULT_TYPE_NODE:
				nodetRet = FormatType.attrNodeEntityTable(attrListData.nodes)

			if attrListData.type == ULTIPA.ResultType.RESULT_TYPE_EDGE:
				edgeRet = FormatType.attrEdgeEntityTable(attrListData.edges)

			PaserAttrRetList.append(
				ULTIPA.PaserAttrListData(attrListData.type, nodes=nodetRet, edges=edgeRet, paths=pathListRet,
										 attrs=attrListRet))
		return PaserAttrRetList

	@classmethod
	def parseAttr(cls, attr, aliasName) -> ULTIPA.AttrAlias:
		valuesList = []
		attr_type = attr.value_type
		# if attr_type == ULTIPA.PropertyType.PROPERTY_NULL:
		# 	return ULTIPA.AttrAlias(alias=aliasName, values=None,
		# 							type=ULTIPA_REQUEST.Property._getStringByPropertyType(attr_type))
		if attr_type == ULTIPA.PropertyType.PROPERTY_LIST:
			valuesList = FormatType.parseAttrListData(attr.values)
			return ULTIPA.AttrAlias(alias=aliasName, values=valuesList,
									type=ULTIPA_REQUEST.Property._getStringByPropertyType(attr_type))

		for att in attr.values:
			_seria = _Serialize(type=attr_type, value=att)
			sdata = _seria.unserialize()
			valuesList.append(sdata)
		return ULTIPA.AttrAlias(alias=aliasName, values=valuesList,
								type=ULTIPA_REQUEST.Property._getStringByPropertyType(attr_type))

	@classmethod
	def parseAttrAlias(cls, attrAlias) -> ULTIPA.AttrAlias:
		return cls.parseAttr(attrAlias.attr, attrAlias.alias)

	@staticmethod
	def attrAlias1(_attrs) -> List[ULTIPA.AttrAlias]:
		attr_list = []
		if _attrs:
			for attr in _attrs:
				# li = []
				# attr_type = attr.attr.property_type
				# if attr_type==ULTIPA.PropertyType.PROPERTY_LIST:
				# 	FormatType.attrListData(attr.attr.values)
				#
				# for att in attr.values:
				# 	_seria = _Serialize(type=attr_type, value=att)
				# 	sdata = _seria.unserialize()
				# 	li.append(sdata)
				# ret = ULTIPA.AttrAlias(alias=attr.alias, values=li,
				# 					   type=ULTIPA_REQUEST.Property._getStringByPropertyType(attr_type))
				attr_list.append(FormatType.parseAttrAlias(attr))
		return attr_list

	@staticmethod
	def attr(attr, timeZone, timeZoneOffset) -> ULTIPA.Attr:
		type = attr.value_type
		result = ULTIPA.Attr(type, None, has_attr_data=False, has_ultipa_data=False,
							 type_desc=ULTIPA_REQUEST.Property._getStringByPropertyType(type))
		result.values = []
		for value in attr.values:
			if type == ULTIPA.PropertyType.PROPERTY_NULL:
				result.has_attr_data = True
				result.values.append(None)
				continue
			if type == ULTIPA.PropertyType.PROPERTY_LIST:
				attrListData = AttrListData()
				attrListData.ParseFromString(value)
				result_type: any = attrListData.type
				if attrListData.is_null:
					result.values.append(None)
					continue

				if result_type == ULTIPA.ResultType.RESULT_TYPE_ATTR:
					attrs = []
					for attr in attrListData.attrs:
						att = FormatType.attr(attr, timeZone, timeZoneOffset)
						if not att.values:
							attrs.append(att.values)
						else:
							attrs.extend(att.values)
					if len(attrs) != 0:
						result.has_attr_data = True
					result.values.append(attrs)

				if result_type == ULTIPA.ResultType.RESULT_TYPE_PATH:
					result.has_ultipa_data = True
					result.values.append(ULTIPA.PaserAttrListData(attrListData.type,
																  paths=FormatType.attrPath(attrListData.paths,
																							timeZone, timeZoneOffset)))

				if result_type == ULTIPA.ResultType.RESULT_TYPE_NODE:
					result.has_ultipa_data = True
					result.values.append(ULTIPA.PaserAttrListData(attrListData.type,
																  nodes=FormatType.attrNodeEntityTable(
																	  attrListData.nodes)))

				if result_type == ULTIPA.ResultType.RESULT_TYPE_EDGE:
					result.has_ultipa_data = True
					result.values.append(ULTIPA.PaserAttrListData(attrListData.type,
																  edges=FormatType.attrEdgeEntityTable(
																	  attrListData.edges)))
			else:
				_seria = _Serialize(type=type, value=value, timeZone=timeZone, timeZoneOffset=timeZoneOffset)
				sdata = _seria.unserialize()
				result.has_attr_data = True
				result.values.append(sdata)
		return result

	@staticmethod
	def attrAlias(_attrs, timeZone, timeZoneOffset) -> List[ULTIPA.AttrNewAlias]:
		attr_list = []
		if _attrs:
			for attr in _attrs:
				attr_data = FormatType.attr(attr.attr, timeZone, timeZoneOffset)
				attr_list.append(ULTIPA.AttrNewAlias(alias=attr.alias, attr=attr_data))
		return attr_list

	@staticmethod
	def arrays(_arrays) -> List[ULTIPA.ArrayAlias]:
		arrays_list = []
		if _arrays:
			for attr in _arrays:
				li = []
				attr_type = attr.property_type
				for att in attr.elements:
					# li.append(att)
					value_li = []
					for el in att.values:
						_seria = _Serialize(type=attr_type, value=el)
						sdata = _seria.unserialize()
						value_li.append(sdata)
					li.append(value_li)
				ret = ULTIPA.ArrayAlias(alias=attr.alias, elements=li)
				arrays_list.append(ret)
		return arrays_list

	@staticmethod
	def resultalias(_arrays) -> List[ULTIPA.ResultAlias]:
		value_dict = []
		if _arrays:
			for value in _arrays:
				value_dict.append(ULTIPA.ResultAlias(value.alias, ResultType.getTypeStr(value.result_type)))
		return value_dict

	@staticmethod
	def explainPlan(_explainPlan) -> List[ULTIPA.ExplainPlan]:
		explainPlanRet = []
		if _explainPlan:
			for value in _explainPlan.plan_nodes:
				explainPlanRet.append(
					ULTIPA.ExplainPlan(value.alias, value.children_num, value.uql, value.infos))
		return explainPlanRet

	# @staticmethod
	# def nodes(_nodes) -> List:
	#     nodeData = []
	#     if _nodes:
	#         for n in _nodes.nodes:
	#             valuesData = {}
	#             for v in n.values:
	#                 valuesData[v.key] = v.value
	#             nData = ULTIPA.Node(n.id, values=valuesData)
	#             nodeData.append((nData))
	#     return nodeData
	#
	# @staticmethod
	# def edges(_edges) -> List:
	#     edgeData = []
	#     if _edges:
	#         for n in _edges.edges:
	#             valuesData = {}
	#             for v in n.values:
	#                 valuesData[v.key] = v.value
	#             eData = ULTIPA.Edge(n.id, n.from_id, n.to_id, values=valuesData)
	#             edgeData.append((eData))
	#     return edgeData

	@staticmethod
	def export_edges(_edges, timeZone, timeZoneOffset) -> List:
		edgeTableData = FormatType.edgeTable(_edges, timeZone, timeZoneOffset)

		return edgeTableData

	@staticmethod
	def export_nodes(_nodes, timeZone, timeZoneOffset) -> List:
		nodeTableData = FormatType.nodeTable(_nodes, timeZone, timeZoneOffset)
		return nodeTableData

	# @staticmethod
	# def path(_paths) -> List[ULTIPA.Path]:
	#     pathAliasesData = []
	#     if _paths:
	#         for path in _paths:
	#             nodeAliasesData = FormatType.nodeTable(path)
	#             edgeAliasesData = FormatType.edgeTable(path)
	#             pathData = ULTIPA.Path(nodes=nodeAliasesData, edges=edgeAliasesData)
	#             pathAliasesData.append(pathData)
	#     return pathAliasesData

	@staticmethod
	def pathAlias(_paths, timeZone, timeZoneOffset) -> [ULTIPA.PathAlias]:
		pathData = []
		if _paths:
			for path in _paths:
				pathAlia = ULTIPA.PathAlias(path.alias)
				for npath in path.paths:
					nodeAliasesData = FormatType.nodeTable(npath, timeZone, timeZoneOffset)
					edgeAliasesData = FormatType.edgeTable(npath, timeZone, timeZoneOffset)
					nodeSchema, edgeSchema = FormatType.pathScheams(npath)
					newPath = ULTIPA.Path(nodes=nodeAliasesData, edges=edgeAliasesData, nodeSchemas=nodeSchema,
										  edgeSchemas=edgeSchema)
					pathAlia.paths.append(newPath)
				pathData.append(pathAlia)
		return pathData

	@staticmethod
	def attrPath(_paths, timeZone, timeZoneOffset) -> [ULTIPA.Path]:
		pathData = []
		if _paths:
			for path in _paths:
				# pathAlia = ULTIPA.PathAlias(path.alias)
				# for npath in path.paths:
				nodeAliasesData = FormatType.nodeTable(path, timeZone, timeZoneOffset)
				edgeAliasesData = FormatType.edgeTable(path, timeZone, timeZoneOffset)
				nodeSchema, edgeSchema = FormatType.pathScheams(path)
				newPath = ULTIPA.Path(nodes=nodeAliasesData, edges=edgeAliasesData, nodeSchemas=nodeSchema,
									  edgeSchemas=edgeSchema)
				pathData.append(newPath)
		return pathData

	@staticmethod
	def pathAlias1(_paths) -> [ULTIPA.PathAlias]:
		if not _paths:
			return []
		pathData = [None] * len(_paths)
		index = -1
		for path in _paths:
			index += 1
			pathAlia = ULTIPA.PathAlias(path.alias)
			for path in path.paths:
				nodeAliasesData = FormatType.nodeTable(path)
				edgeAliasesData = FormatType.edgeTable(path)
				pathAlia.paths.append(
					ULTIPA.Path(nodes=nodeAliasesData, edges=edgeAliasesData, nodeSchemas=None, edgeSchemas=None))
			pathData[index] = pathAlia
		return pathData

	@staticmethod
	def Response(_res, host: str = None) -> ULTIPA_RESPONSE.Response:
		status = FormatType.status(_res.status, host)
		res = ULTIPA_RESPONSE.Response(status)
		return res

	@staticmethod
	def mergeUqlResponse(mergeRes: ULTIPA_RESPONSE.Response, res: ULTIPA_RESPONSE.Response):
		if not mergeRes.data:
			mergeRes = copy.deepcopy(res)
			return mergeRes
		if res.data.paths:
			mergeRes.data.paths = DataMerge.concat(mergeRes.data.paths, res.data.paths)
		if res.data.nodes:
			mergeRes.data.nodes = DataMerge.concat(mergeRes.data.nodes, res.data.nodes, 'nodes')
		if res.data.edges:
			mergeRes.data.edges = DataMerge.concat(mergeRes.data.edges, res.data.edges, 'edges')
		if res.data.attrs:
			mergeRes.data.attrs = DataMerge.concat(mergeRes.data.attrs, res.data.attrs, 'values')
		if res.data.tables:
			mergeRes.data.tables = DataMerge.concat(mergeRes.data.tables, res.data.tables, "table_name", ["headers"])
		if res.data.explainPlan:
			mergeRes.data.explainPlan = DataMerge.concat(mergeRes.data.explainPlan, res.data.explainPlan)
		if res.data.resultAlias:
			mergeRes.data.resultAlias = DataMerge.concat(mergeRes.data.resultAlias, res.data.resultAlias)
		if res.statistics:
			mergeRes.statistics = DataMerge.concat(mergeRes.statistics, res.statistics)

		return mergeRes

	@staticmethod
	def response(uql_response: ULTIPA_RESPONSE.Response, uqlReply, timeZone,
				 timeZoneOffset) -> ULTIPA_RESPONSE.Response:
		attrs = FormatType.attrAlias(uqlReply.attrs, timeZone, timeZoneOffset)

		attrs_attrs = []
		attrs_map = {}

		def addAttributes(alias: str, type: ULTIPA.ResultType, values: any, dataMap: HasDataMap) -> None:
			if attrs_map.get(alias) is None:
				if dataMap.has_attr_data:
					type = ULTIPA.ResultType.RESULT_TYPE_ATTR
				attralias = ULTIPA.AttrAlias(alias=alias, type=type, type_desc=ULTIPA.ResultType.getTypeStr(type),
											 values=[])
				attrs_map[alias] = attralias
				attrs_attrs.append(attralias)
			if type == ULTIPA.ResultType.RESULT_TYPE_ATTR and dataMap.only_attr_list:
				attrs_map[alias].values = values
			else:
				attrs_map[alias].values.append(values)

		for attrAlias in attrs:
			alias = attrAlias.alias
			has_attr_data = attrAlias.attr.has_attr_data
			has_ultipa_data = attrAlias.attr.has_ultipa_data
			only_attr_list = has_attr_data and not has_ultipa_data
			dataMap = HasDataMap(has_ultipa_data=has_ultipa_data, has_attr_data=has_attr_data,
								 only_attr_list=only_attr_list)
			if attrAlias.attr.type == ULTIPA.PropertyType.PROPERTY_LIST:
				if only_attr_list:
					addAttributes(alias, ULTIPA.ResultType.RESULT_TYPE_ATTR, attrAlias.attr.values, dataMap)
					continue

				for row in attrAlias.attr.values:
					if not row or not row.type:
						addAttributes(alias, ULTIPA.ResultType.RESULT_TYPE_ATTR, row, dataMap)
						continue

					if not isinstance(row, ULTIPA.PaserAttrListData):
						addAttributes(alias, ULTIPA.ResultType.RESULT_TYPE_ATTR, row, dataMap)
						continue

					if row.type == ULTIPA.ResultType.RESULT_TYPE_NODE:
						addAttributes(alias, row.type, row.nodes, dataMap)

					elif row.type == ULTIPA.ResultType.RESULT_TYPE_EDGE:
						addAttributes(alias, row.type, row.edges, dataMap)

					elif row.type == ULTIPA.ResultType.RESULT_TYPE_PATH:
						addAttributes(alias, row.type, row.paths, dataMap)

			else:
				addAttributes(alias, ULTIPA.ResultType.RESULT_TYPE_ATTR, attrAlias.attr.values, dataMap)

		status = FormatType.status(uqlReply.status)
		tables = FormatType.tables(uqlReply.tables, timeZone, timeZoneOffset)
		paths = FormatType.pathAlias(uqlReply.paths, timeZone, timeZoneOffset)
		nodes = FormatType.nodeAliases(uqlReply.nodes, timeZone, timeZoneOffset)  # ForamtType.nodeAliases
		edges = FormatType.edgeAliases(uqlReply.edges, timeZone, timeZoneOffset)
		attrs = attrs_attrs
		# arrays = FormatType.arrays(uqlReply.arrays)
		statistics = FormatType.statistics(uqlReply.statistics, timeZone, timeZoneOffset)
		resultAlias = FormatType.resultalias(uqlReply.alias)
		explainPlan = FormatType.explainPlan(uqlReply.explain_plan)
		baseReply = ULTIPA.BaseUqlReply(paths=paths, nodes=nodes, edges=edges, tables=tables,
										attrs=attrs, resultAlias=resultAlias, explainPlan=explainPlan)
		uql_response.status = status
		uql_response.statistics = statistics
		uql_response.data = baseReply
		uql_response.aliases = resultAlias
		return uql_response

	@staticmethod
	def uqlResponse(_res, timeZone, timeZoneOffset) -> ULTIPA_RESPONSE.UltipaResponse:
		uql_response = ULTIPA_RESPONSE.Response()
		ultipa_response = ULTIPA_RESPONSE.UltipaResponse()
		for uqlReply in _res:
			status = FormatType.status(uqlReply.status)
			uql_response = FormatType.response(uql_response, uqlReply, timeZone, timeZoneOffset)
			ret = ULTIPA.UqlReply(dataBase=uql_response.data)

			if status.code != ULTIPA.Code.SUCCESS:
				ultipa_response.status = uql_response.status
				ultipa_response.req = uql_response.req
				return ultipa_response

			ultipa_response.items = ret._aliasMap
			# ultipa_response._data = ret.datas
			ultipa_response.status = uql_response.status
			ultipa_response.req = uql_response.req
			ultipa_response.statistics = uql_response.statistics
			yield ultipa_response

	@staticmethod
	def uqlMergeResponse(_res, timeZone, timeZoneOffset) -> ULTIPA_RESPONSE.UltipaResponse:
		uql_response = ULTIPA_RESPONSE.Response()
		mergeRes = ULTIPA_RESPONSE.Response()
		ultipa_response = ULTIPA_RESPONSE.UltipaResponse()
		for uqlReply in _res:
			status = FormatType.status(uqlReply.status)
			uql_response = FormatType.response(uql_response, uqlReply, timeZone, timeZoneOffset)
			if status.code != ULTIPA.Code.SUCCESS:
				ultipa_response.status = uql_response.status
				ultipa_response.req = uql_response.req
				return ultipa_response
			mergeRes = FormatType.mergeUqlResponse(mergeRes, uql_response)

		ret = ULTIPA.UqlReply(dataBase=mergeRes.data)
		ultipa_response.items = ret._aliasMap
		ultipa_response.explainPlan = ret.explainPlan
		# ultipa_response._data = ret.datas
		ultipa_response.status = uql_response.status
		ultipa_response.req = uql_response.req
		ultipa_response.aliases = uql_response.aliases
		ultipa_response.statistics = uql_response.statistics
		return ultipa_response

	@staticmethod
	def downloadResponse(_res) -> ULTIPA_RESPONSE.Response:
		for uqlReply in _res:
			status = FormatType.status(uqlReply.status)
			data = FormatType.status(uqlReply.chunk)
			total_time = uqlReply.total_time_cost
			engine_time = uqlReply.total_time_cost
			res = ULTIPA_RESPONSE.Response(status, total_time, engine_time, data)
			return res

	@staticmethod
	def exportResponse(_res, timeZone, timeZoneOffset) -> ULTIPA_RESPONSE.Response:
		nodedata = []
		edgedata = []
		res = ULTIPA_RESPONSE.Response()
		for uqlReply in _res:
			# res.statistics=FormatType.statistics(uqlReply.statistics)
			res.status = FormatType.status(uqlReply.status)
			if uqlReply.node_table:
				nodedata = FormatType.export_nodes(uqlReply, timeZone, timeZoneOffset)
			if uqlReply.edge_table:
				edgedata = FormatType.export_edges(uqlReply, timeZone, timeZoneOffset)
			if nodedata:
				uql = ULTIPA.ExportReply(data=nodedata)
				res.data = uql.data
			if edgedata:
				uql = ULTIPA.ExportReply(data=edgedata)
				res.data = uql.data
			break
		return res

	@staticmethod
	def graphPrivileges(graphPrivileges: '[object]'):
		new_graphPrivileges = []

		if graphPrivileges:
			for gp in graphPrivileges:
				graphDcit = {}
				graphDcit.update({'name': list(gp.keys())[0]})
				graphDcit.update({'values': list(gp.values())[0]})
				new_graphPrivileges.append(graphDcit)

		return new_graphPrivileges


if __name__ == '__main__':
	ls = [{"name": 123, "b": 1}, {"a": 1}, {"name": 123}, {"sdfasdf": 123234}]
	for i in ls:
		print(list(i.keys()))
