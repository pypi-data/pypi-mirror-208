from ultipa.types import ULTIPA
from ultipa.types.types import BaseModel, OrderType, UltipaEquation
from ultipa.utils import common as COMMON
from ultipa.utils.ufilter import ufilter as FILTER
from ultipa.utils.ufilter.new_ufilter import *


class OrderBy:
	def __init__(self, schemaName: str, propertyName: str, orderType: OrderType):
		self.schemaName = '@' + schemaName
		self.propertyName = propertyName
		self.orderType = orderType.value

	@property
	def toString(self):
		return "%s.%s %s" % (self.schemaName, self.propertyName, self.orderType)


class GroupBy:
	def __init__(self, schemaName: str, propertyName: str):
		self.schemaName = '@' + schemaName
		self.propertyName = propertyName

	@property
	def toString(self):
		return "%s.%s" % (self.schemaName, self.propertyName)


class CommonSchema:
	def __init__(self, schema: str, property: str):
		self.schemaName = '@' + schema
		self.propertyName = property

	@property
	def toString(self):
		return "%s.%s" % (self.schemaName, self.propertyName)


class UltipaPath:
	def __init__(self, nodeSchema: List[CommonSchema], edgeSchema: List[CommonSchema]):
		self.nodeSchema = nodeSchema
		self.edgeSchema = edgeSchema

	@property
	def toString(self):
		if self.nodeSchema == '*':
			nodeSchema = '*'
		else:
			nodeSchema = ','.join([i.toString for i in self.nodeSchema])

		if self.edgeSchema == '*':
			edgeSchema = '*'
		else:
			edgeSchema = ','.join([i.toString for i in self.edgeSchema])

		return "{%s}{%s}" % (nodeSchema, edgeSchema)


class UltipaReturn:
	def __init__(self, schemaName: str, propertyName: str, equation: UltipaEquation = None, alias: List[str] = None,
				 path: UltipaPath = None):
		self.schemaName = '@' + schemaName
		self.propertyName = propertyName
		self.equation = equation
		self.alias = alias
		self.path = path

	@property
	def toString(self):
		if self.path:
			return "path%s" % (self.path.toString)
		if self.alias and self.propertyName and not self.schemaName and not self.equation:
			return "%s{%s}" % (self.alias, ','.join(self.propertyName))

		if self.equation and self.alias:
			return "%s(%s.%s) as %s" % (self.equation.value, self.schemaName, self.propertyName, self.alias)
		return "{%s.%s}" % (self.schemaName, self.propertyName)


class Return:
	def __init__(self, alias: str, propertys: List[str] = None, allProperties: bool = False, limit: int = COMMON.LIMIT):
		if propertys is None:
			propertys = []
		self.aliasName = alias
		self.propertys = propertys
		self.all = allProperties
		self.limit = limit

	@property
	def toString(self):
		if self.all:
			return "%s{%s} limit %s" % (self.aliasName, "*", self.limit)
		if len(self.propertys) == 1:
			return "%s.%s limit %s" % (self.aliasName, self.propertys[0], self.limit)
		else:
			return "%s{%s} limit %s" % (self.aliasName, ','.join(self.propertys), self.limit)


# class GraphPrivilege:
#     def __init__(self,graphName, value: [str]):
#         self.graphName=graphName
#         self.value=value
#
#     def toDict(self):
#         return "{'%s':%s}"%(self.graphName,self.value)


class CreateUser:
	def __init__(self, username: str, password: str, graphPrivileges: [dict] = None,
				 systemPrivileges: List[str] = None, policies: List[str] = None):
		self.username = username
		self.password = password
		self.graph_privileges = graphPrivileges
		self.system_privileges = systemPrivileges
		self.policies = policies


class DropUser:
	def __init__(self, username: str):
		self.username = username


class AlterUser(CreateUser):
	def __init__(self, username: str, password: str = None, graph_privileges: [dict] = None,
				 system_privileges: List[str] = None, policies: List[str] = None):
		super().__init__(username, password, graph_privileges, system_privileges, policies)


class GetUser:
	def __init__(self, username: str):
		self.username = username


class GetUserSetting:
	def __init__(self, username: str, type: str):
		self.username = username
		self.type = type


class SetUserSetting:
	def __init__(self, username: str, type: str, data: str):
		self.username = username
		self.type = type
		self.data = data


class Kill:
	def __init__(self, id: str = None, all: bool = False):
		self.id = id
		self.all = all


class ShowTask:
	def __init__(self, id: int = None, name: str = None, limit: int = None, status: str = ''):
		self.id = id
		self.limit = limit
		self.name = name
		self.status = status


class ClearTask:
	def __init__(self, id: int = None, name: str = None, status: str = None, all: bool = False):
		self.id = id
		self.name = name
		self.status = status
		self.all = all


class PauseTask:
	def __init__(self, id: int = None, all: bool = None):
		self.id = id
		self.all = all


class ResumeTask:
	def __init__(self, id: int = None, all: bool = None):
		self.id = id
		self.all = all


class StopTask():
	def __init__(self, id: int = None, all: bool = False):
		self.id = id
		self.all = all


class Header:
	def __init__(self, name: str, type: ULTIPA.PropertyType):
		self.name = name
		self.type = type


class InsertNodeBulk:
	def __init__(self, schema: str, rows: List[dict], insertType: ULTIPA.InsertType, silent: bool = False,
				 batch: bool = False, n: int = 100, timeZone=None, timeZoneOffset=None):
		# self.headers = headers
		self.schema = schema
		self.rows = rows
		self.silent = silent
		self.insertType = insertType
		self.batch = batch
		self.n = n
		self.timeZone = timeZone
		self.timeZoneOffset = timeZoneOffset


class InsertEdgeBulk:
	def __init__(self, schema: str, rows: List[dict], insertType: ULTIPA.InsertType, silent: bool = False,
				 create_node_if_not_exist: bool = False, batch: bool = False, n: int = 100, timeZone=None,
				 timeZoneOffset=None):
		self.schema = schema
		self.rows = rows
		self.silent = silent
		self.create_node_if_not_exist = create_node_if_not_exist
		self.insertType = insertType
		self.batch = batch
		self.n = n
		self.timeZone = timeZone
		self.timeZoneOffset = timeZoneOffset


class InsertNode:
	def __init__(self, nodes: List[dict], schema: str, overwrite: bool = False, upsert: bool = False,
				 isReturnID: bool = True):
		self.nodes = nodes
		self.schemaName = '@' + schema
		self.overwrite = overwrite
		self.upsert = upsert
		self.isReturnID = isReturnID

	def setSchema(self, schema: str):
		self.schemaName = '@' + schema


class InsertEdge:
	def __init__(self, edges: List[dict], schema: str, overwrite: bool = False, upsert: bool = False,
				 isReturnID: bool = True):
		self.edges = edges
		self.schemaName = '@' + schema
		self.overwrite = overwrite
		self.upsert = upsert
		self.isReturnID = isReturnID

	def setSchema(self, schema: str):
		self.schemaName = '@' + schema


class SearchNode:
	def __init__(self, select: Return, id=None,
				 filter: UltipaFilter or list or str = None):
		if id is None:
			id = []
		self.id = id
		self.filter = filter
		self.select = select


# self.skip = skip
# if order_by:
#     self.order_by = order_by.toString
# if group_by:
#     self.group_by = group_by.toString


class SearchEdge(SearchNode):
	pass


class UpdateNode:
	def __init__(self, values: dict, uuid: [int] = None, filter: UltipaFilter = None, silent: bool = False):
		if uuid is None:
			uuid = []
		self.id = uuid
		self.filter = filter
		self.values = values
		self.silent = silent


class UpdateEdge(UpdateNode):
	pass


class DeleteNode:
	def __init__(self, uuid: [int] = None, filter: UltipaFilter = None, silent: bool = False):
		if uuid is None:
			uuid = []
		self.id = uuid
		self.filter = filter
		self.silent = silent


class DeleteEdge(DeleteNode):
	pass


class Graph:
	def __init__(self, graph, description: str = None):
		self.graph = graph
		self.description = description


class AlterGraph:
	def __init__(self, oldGraphName: str, newGraphName: str, newDescription: str = None):
		self.oldGraphName = oldGraphName
		self.newGraphName = newGraphName
		self.newDescription = newDescription


class Retry:
	def __init__(self, current: int = 0, max: int = 3):
		self.current = current
		self.max = max


class RequestConfig:

	def __init__(self, graphName: str = '', timeout: int = 3600, retry: Retry = Retry(),
				 stream: bool = False, host: str = None, useMaster: bool = False, threadNum: int = None,
				 timeZone: str = None, timeZoneOffset: int = None):
		self.graphName = graphName
		self.timeoutWithSeconds = timeout
		self.retry = retry
		self.stream = stream
		self.useHost = host
		self.useMaster = useMaster
		self.threadNum = threadNum
		self.timeZone = timeZone
		self.timeZoneOffset = timeZoneOffset


class InsertConfig(RequestConfig):
	def __init__(self, insertType: ULTIPA.InsertType, graphName: str = '', timeout: int = 3600,
				 retry: Retry = Retry(), stream: bool = False, useHost: str = None, useMaster: bool = False,
				 CreateNodeIfNotExist: bool = False, timeZone=None, timeZoneOffset=None, **kwargs):
		super().__init__(graphName, timeout, retry, stream, useHost, useMaster, timeZone=timeZone,
						 timeZoneOffset=timeZoneOffset)
		self.insertType = insertType
		if kwargs.get("silent") is not None:
			self.silent = kwargs.get("silent")
		else:
			self.silent = True
		if kwargs.get("batch") is not None:
			self.batch = kwargs.get("batch")
		if kwargs.get("n") is not None:
			self.n = kwargs.get("n")
		if kwargs.get("timeoutWithSeconds") is not None:
			self.timeoutWithSeconds = kwargs.get("timeoutWithSeconds")
		self.createNodeIfNotExist = CreateNodeIfNotExist


class Common(InsertConfig):
	...


class LTE:

	def __init__(self, schemaName: CommonSchema, type: ULTIPA.DBType):
		'''LTE UFE Node and Edge property'''
		self.schemaName = schemaName
		self.type = type


class UFE(LTE):
	...


class Property:
	def __init__(self, type: ULTIPA.DBType, name: str = ''):
		self.type = type
		self.name = name


class GetProperty:
	def __init__(self, type: ULTIPA.DBType, schema: str = None):
		self.type = type
		self.schemaName = schema

	def __str__(self):
		return '@' + self.schemaName


class CreateProperty(Property):
	def __init__(self, type: ULTIPA.DBType, commonSchema: CommonSchema,
				 propertyType: ULTIPA.CreatePropertyType = ULTIPA.CreatePropertyType.PROPERTY_STRING,
				 description: str = '', subTypes: List[ULTIPA.CreatePropertyType] = None):
		super().__init__(type)
		self.propertyType = propertyType
		self.subTypes = subTypes
		self.description = description
		self.schemaName = commonSchema


class DropProperty(Property):
	def __init__(self, type: ULTIPA.DBType, commonSchema: CommonSchema):
		super().__init__(type)
		self.schemaName = commonSchema


class AlterProperty(Property):
	def __init__(self, type: ULTIPA.DBType, commonSchema: CommonSchema, newName: str, newDescription: str = ''):
		super().__init__(type)
		self.new_name = newName
		self.description = newDescription
		self.schemaName = commonSchema


class CreateSchema:
	def __init__(self, name: str, type: ULTIPA.DBType, description: str = None):
		self.schemaName = name
		self.type = type
		self.description = description


class ShowSchema:
	def __init__(self, type: ULTIPA.DBType = None, schema: str = None):
		self.schemaType = type
		self.schemaName = schema


class AlterSchema:
	def __init__(self, type: ULTIPA.DBType, schema: str, newName: str, newDescription: str = ''):
		self.type = type
		self.schemaName = schema
		self.new_schemaName = newName
		self.description = newDescription


class DropSchema:
	def __init__(self, type: ULTIPA.DBType, schema: str):
		self.type = type
		self.schemaName = schema


class Index(CommonSchema):
	def __init__(self, type: ULTIPA.DBType, schema: str, property: str):
		super().__init__(schema=schema, property=property)
		self.DBtype = type


class ShowIndex():
	def __init__(self, type: ULTIPA.DBType):
		self.DBtype = type


class ShowFulltext(ShowIndex):
	def __init__(self, type: ULTIPA.DBType):
		super().__init__(type=type)


class CreateIndex(Index):
	def __init__(self, type: ULTIPA.DBType, schema: str, property: str):
		super().__init__(type, schema, property)


class CreateFulltext(Index):
	def __init__(self, type: ULTIPA.DBType, schema: str, property: str, name: str):
		super().__init__(type, schema, property)
		self.name = name


class DropIndex(Index):
	def __init__(self, type: ULTIPA.DBType, schema: str, property: str):
		super().__init__(type, schema, property)


class DropFulltext:
	def __init__(self, type: ULTIPA.DBType, name: str = ""):
		self.fulltextName = name
		self.DBtype = type


#
# class UpdateEdge:
#     def __init__(self,params:'dict', id: "str"='',  filter: 'dict'=None,):
#         ''''''
#         self.id = id
#         self.set = params
#         self.filter = filter


class SearchAB:
	def __init__(self, src: int = None, dest: int = None, depth: int = COMMON.DEPTH, limit: int = COMMON.LIMIT,
				 select: List[str] = None,
				 select_node_properties: List[str] = None, select_edge_properties: List[str] = None,
				 shortest: bool = False, nodeFilter: dict = None,
				 edgeFilter: dict = None, path_ascend: str = '', path_descend: str = '',
				 direction: ULTIPA.DirectionType = None, turbo: bool = False, osrc: str = '',
				 odest: str = '', no_circle: bool = False, boost: bool = False):
		self.src = src
		self.dest = dest
		self.depth = depth
		self.shortest = shortest
		self.node_filter = nodeFilter
		self.edge_filter = edgeFilter
		self.path_ascend = path_ascend
		self.path_descend = path_descend
		self.direction = direction
		self.no_circle = no_circle


class Searchkhop:
	def __init__(self, src: int = None, depth: int = COMMON.DEPTH, limit: int = COMMON.LIMIT,
				 select: List[str] = None, select_node_properties: List[str] = None,
				 select_edge_properties: List[str] = None,
				 node_filter: dict = None, edge_filter: dict = None, direction: ULTIPA.DirectionType = None,
				 turbo: bool = False, osrc: str = ''):
		self.src = src
		self.depth = depth
		self.limit = limit
		self.select = select
		self.select_node_properties = select_node_properties
		self.select_edge_properties = select_edge_properties
		self.node_filter = node_filter
		self.edge_filter = edge_filter
		self.direction = direction
		self.turbo = turbo
		self.osrc = osrc


class Download:
	def __init__(self, fileName: str, taskId: str, savePath: str = None):
		self.fileName = fileName
		self.taskId = taskId
		self.savePath = savePath


class Policy:

	def __init__(self, name: str, graphPrivileges: dict = None, systemPrivileges: List[str] = None,
				 policies: List[str] = None):
		self.name = name
		self.graph_privileges = graphPrivileges
		self.system_privileges = systemPrivileges
		self.policies = policies


class CreatePolicy(Policy):
	pass


class AlterPolicy(Policy):
	pass


class GetPolicy:
	def __init__(self, name: str):
		self.name = name


class DropPolicy(GetPolicy):
	pass


class GrantPolicy:
	def __init__(self, username: str = '', graphPrivileges: dict = None,
				 systemPrivileges: List[str] = None, policies: List[str] = None):
		self.username = username
		self.graph_privileges = graphPrivileges
		self.system_privileges = systemPrivileges
		self.policies = policies


class RevokePolicy(GrantPolicy):
	pass


class NodeSpread:
	def __init__(self, src: int = None, depth: int = COMMON.DEPTH, limit: int = COMMON.LIMIT,
				 select: List[str] = None, selectNodeProperties: List[str] = None,
				 selectEdgeProperties: List[str] = None, nodeFilter: FILTER = None, edgeFilter: FILTER = None,
				 spread_type: str = None,
				 direction: ULTIPA.DirectionType = None, osrc: str = None):
		self.src = src
		self.depth = depth
		self.limit = limit
		self.select = select
		self.select_node_properties = selectNodeProperties
		self.select_edge_properties = selectEdgeProperties
		self.node_filter = nodeFilter
		self.edge_filter = edgeFilter
		self.spread_type = spread_type
		self.direction = direction
		self.osrc = osrc


class AutoNet:
	def __init__(self, srcs: List[int], dests: List[int] = None, depth: int = COMMON.DEPTH,
				 limit: int = COMMON.LIMIT,
				 select: List[str] = None, selectNodeProperties: List[str] = None,
				 selectEdgeProperties: List[str] = None,
				 shortest: bool = False, nodeFilter: FILTER = None, edgeFilter: FILTER = None,
				 turbo: bool = False, noCircle: bool = False, boost: bool = False):
		self.srcs = srcs
		self.dests = dests
		self.depth = depth
		self.limit = limit
		self.select = select
		self.select_node_properties = selectNodeProperties
		self.select_edge_properties = selectEdgeProperties
		self.shortest = shortest
		self.node_filter = nodeFilter
		self.edge_filter = edgeFilter
		self.turbo = turbo
		self.no_circle = noCircle
		self.boost = boost


class Export:
	def __init__(self, type: ULTIPA.DBType, limit: int, schema: str, properties: List[str] = None):
		self.type = type
		self.limit = limit
		self.properties = properties
		self.schema = schema


class TEdgeItem:
	e = 'e'
	le = 'le'
	re = 're'


class TNodeItem:
	n = 'n'


class TemplateBaseItem:
	def __init__(self, name, alias: str, filter=None):
		self.name = name
		self.alias = alias
		self.filter = filter


class TemplateEdgeItem(TemplateBaseItem):
	def __init__(self, name: TEdgeItem, alias: str = '', filter=None, nodeFilter=None, steps: List[str] = None):
		super().__init__(name=name, alias=alias, filter=filter)
		self.node_filter = nodeFilter
		self.steps = steps


class TemplateNodeItem(TemplateBaseItem):
	...


class Template:
	def __init__(self, alias: str, items: List[TemplateEdgeItem or TemplateNodeItem], limit: int, _return,
				 order_by: any = None, isKhopTemplate: bool = False, select: list = None
				 ):
		self.alias = alias
		self.items = items
		self.limit = limit
		self.order_by = order_by
		self._return = _return
		self.isKhopTemplate = isKhopTemplate
		self.select = select


class Truncate:
	def __init__(self, graph: str, truncateType: ULTIPA.TruncateType = None, allData: bool = False, schema: str = None):
		self.dbType = truncateType
		self.graphSetName = graph
		self.all = allData
		self.schema = schema


class Mount:
	def __init__(self, graph: str):
		self.graph = graph


class Unmount:
	def __init__(self, graph: str):
		self.graph = graph


class InstallAlgo:
	# def __init__(self, fileName: str, data: bytes, md5: str):
	#     self.fileName = fileName
	#     self.data = data
	#     self.md5 = md5
	def __init__(self, configPath: str, soPath: str):
		self.configPath = configPath
		self.soPath = soPath


class InstallExtaAlgo(InstallAlgo):
	...


class UninstallAlgo:

	def __init__(self, algoName: str):
		self.algoName = algoName


class UninstallExtaAlgo(UninstallAlgo):
	...


class Property:
	PropertyMap = {
		"string": ULTIPA.PropertyType.PROPERTY_STRING,
		"int32": ULTIPA.PropertyType.PROPERTY_INT32,
		"int64": ULTIPA.PropertyType.PROPERTY_INT64,
		"uint32": ULTIPA.PropertyType.PROPERTY_UINT32,
		"uint64": ULTIPA.PropertyType.PROPERTY_UINT64,
		"float": ULTIPA.PropertyType.PROPERTY_FLOAT,
		"double": ULTIPA.PropertyType.PROPERTY_DOUBLE,
		"datetime": ULTIPA.PropertyType.PROPERTY_DATETIME,
		"timestamp": ULTIPA.PropertyType.PROPERTY_TIMESTAMP,
		"text": ULTIPA.PropertyType.PROPERTY_TEXT,
		"_id": ULTIPA.PropertyType.PROPERTY_ID,
		"_uuid": ULTIPA.PropertyType.PROPERTY_UUID,
		"_from": ULTIPA.PropertyType.PROPERTY_FROM,
		"_to": ULTIPA.PropertyType.PROPERTY_TO,
		"_from_uuid": ULTIPA.PropertyType.PROPERTY_FROM_UUID,
		"_to_uuid": ULTIPA.PropertyType.PROPERTY_TO_UUID,
		"_ignore": ULTIPA.PropertyType.PROPERTY_IGNORE,
		"unset": ULTIPA.PropertyType.PROPERTY_UNSET,
		"point": ULTIPA.PropertyType.PROPERTY_POINT,
		"decimal": ULTIPA.PropertyType.PROPERTY_DECIMAL,
		"list": ULTIPA.PropertyType.PROPERTY_LIST,
		"set": ULTIPA.PropertyType.PROPERTY_SET,
		"map": ULTIPA.PropertyType.PROPERTY_MAP,
		"null": ULTIPA.PropertyType.PROPERTY_NULL,
	}

	PropertyReverseMap = {
		ULTIPA.PropertyType.PROPERTY_STRING: "string",
		ULTIPA.PropertyType.PROPERTY_INT32: "int32",
		ULTIPA.PropertyType.PROPERTY_INT64: "int64",
		ULTIPA.PropertyType.PROPERTY_UINT32: "uint32",
		ULTIPA.PropertyType.PROPERTY_UINT64: "uint64",
		ULTIPA.PropertyType.PROPERTY_FLOAT: "float",
		ULTIPA.PropertyType.PROPERTY_DOUBLE: "double",
		ULTIPA.PropertyType.PROPERTY_DATETIME: "datetime",
		ULTIPA.PropertyType.PROPERTY_TIMESTAMP: "timestamp",
		ULTIPA.PropertyType.PROPERTY_TEXT: "text",
		ULTIPA.PropertyType.PROPERTY_ID: "_id",
		ULTIPA.PropertyType.PROPERTY_UUID: "_uuid",
		ULTIPA.PropertyType.PROPERTY_FROM: "_from",
		ULTIPA.PropertyType.PROPERTY_TO: "_to",
		ULTIPA.PropertyType.PROPERTY_FROM_UUID: "_from_uuid",
		ULTIPA.PropertyType.PROPERTY_TO_UUID: "_to_uuid",
		ULTIPA.PropertyType.PROPERTY_IGNORE: "_ignore",
		ULTIPA.PropertyType.PROPERTY_UNSET: "unset",
		ULTIPA.PropertyType.PROPERTY_POINT: "point",
		ULTIPA.PropertyType.PROPERTY_DECIMAL: "decimal",
		ULTIPA.PropertyType.PROPERTY_LIST: "list",
		ULTIPA.PropertyType.PROPERTY_SET: "set",
		ULTIPA.PropertyType.PROPERTY_MAP: "map",
		ULTIPA.PropertyType.PROPERTY_NULL: "null",
	}

	def __init__(self, name: str, type: ULTIPA.PropertyType = None, desc: str = None,
				 subTypes: List[ULTIPA.PropertyType] = None):
		self.name = name
		self.desc = desc
		self.type = type
		self.subTypes = subTypes

	def setSubTypesbyType(self, type: str):
		if "string" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_STRING]

		if "int32" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_INT32]

		if "uint32" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_UINT32]

		if "int64" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_INT64]

		if "uint64" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_UINT64]

		if "float" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_FLOAT]

		if "double" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_DOUBLE]

		if "datetime" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_DATETIME]

		if "timestamp" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_TIMESTAMP]

		if "text" in type:
			self.subTypes = [ULTIPA.PropertyType.PROPERTY_TEXT]

	def isIdType(self) -> bool:
		idTypes = [
			ULTIPA.PropertyType.PROPERTY_ID,
			ULTIPA.PropertyType.PROPERTY_TO,
			ULTIPA.PropertyType.PROPERTY_UUID,
			ULTIPA.PropertyType.PROPERTY_FROM,
			ULTIPA.PropertyType.PROPERTY_FROM_UUID,
			ULTIPA.PropertyType.PROPERTY_TO_UUID,
		]
		return self.type in idTypes

	def isIgnore(self):
		return self.type == ULTIPA.PropertyType.PROPERTY_IGNORE

	def setTypeStr(self, value):
		self.type = self.getStringByPropertyType(value)

	def setTypeInt(self, value):
		self.type = self.getPropertyTypeByString(value)

	def getStringType(self):
		return self.getStringByPropertyType(self.type)

	def getPropertyTypeByString(self, v):
		if not self.PropertyMap.get(v):
			if "[" in v:
				self.setSubTypesbyType(v)
				return ULTIPA.PropertyType.PROPERTY_LIST

		return self.PropertyMap.get(v)

	def getStringByPropertyType(self, v):
		return self.PropertyReverseMap[v]

	@staticmethod
	def _getStringByPropertyType(v):
		return Property.PropertyReverseMap[v]

	@staticmethod
	def _getPropertyTypeByString(v):
		return Property.PropertyMap.get(v)




class Schema:

	def __init__(self, name: str, properties: List[Property], desc: str = None, type: str = None,
				 DBType: ULTIPA.DBType = None, total: int = None):
		self.name = name
		self.properties = properties
		self.desc = desc
		self.type = type
		self.DBType = DBType
		self.total = total

	def getProperty(self, name: str):
		find = list(filter(lambda x: x.get('name') == name, self.properties))
		if find:
			return find[0]
		return None


class Batch:
	Nodes: List[ULTIPA.EntityRow]
	Edges: List[ULTIPA.EntityRow]
	Schema: Schema

	def __init__(self, Schema: Schema = None, Nodes: List[ULTIPA.EntityRow] = None,
				 Edges: List[ULTIPA.EntityRow] = None):
		if Nodes is None:
			Nodes = []
		if Edges is None:
			Edges = []
		self.Nodes = Nodes
		self.Edges = Edges
		self.Schema = Schema


class InsertNodeTable:
	def __init__(self, schemas: List[Schema], nodeRows: List[ULTIPA.Node]):
		self.schemas = schemas
		self.nodeRows = nodeRows


class InsertEdgeTable:
	def __init__(self, schemas: List[Schema], edgeRows: List[ULTIPA.Edge]):
		self.schemas = schemas
		self.edgeRows = edgeRows
