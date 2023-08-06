# -*-coding:utf-8-*-
import uuid
import json
from enum import Enum
from typing import List, Dict
from ultipa.proto import ultipa_pb2
from typing import TypeVar
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertToListAnyObject, convertTableToDict, convertToAnyObject, \
	convertAlgoList2AnyObject
from ultipa.utils.errors import ParameterException
from ultipa.utils.logger import LoggerConfig


# T = TypeVar('T')


class DBType:
	DBNODE = ultipa_pb2.DBNODE
	DBEDGE = ultipa_pb2.DBEDGE


class TruncateType:
	NODES = 'nodes'
	EDGES = 'edges'


class DirectionType:
	left = 'left'
	right = 'right'


class CreatePropertyType:
	PROPERTY_INT = 'int32'
	PROPERTY_STRING = 'string'
	PROPERTY_FLOAT = 'float'
	PROPERTY_DOUBLE = 'double'
	PROPERTY_UINT32 = 'uint32'
	PROPERTY_INT64 = 'int64'
	PROPERTY_UINT64 = 'uint64'
	PROPERTY_DATETIME = 'datetime'
	PROPERTY_TIMESTAMP = 'timestamp'
	PROPERTY_TEXT = 'text'
	PROPERTY_UNSET = "unset"
	PROPERTY_POINT = "point"
	PROPERTY_DECIMAL = "decimal"
	PROPERTY_LIST = "list"
	PROPERTY_SET = "set"
	PROPERTY_MAP = "map"


# PROPERTY_BLOB = 'BLOB'


class TaskStatus:
	TASK_WAITING = 0
	TASK_COMPUTING = 1
	TASK_WRITEBACKING = 2
	TASK_DONE = 3
	TASK_FAILED = 4
	TASK_STOP = 5


TaskStatusString = {
	TaskStatus.TASK_WAITING: "TASK_WAITING",
	TaskStatus.TASK_COMPUTING: "TASK_COMPUTING",
	TaskStatus.TASK_WRITEBACKING: "TASK_WRITEBACKING",
	TaskStatus.TASK_DONE: "TASK_DONE",
	TaskStatus.TASK_FAILED: "TASK_FAILED",
	TaskStatus.TASK_STOP: "TASK_STOP"
}


class InsertType:
	NORMAL = ultipa_pb2.NORMAL
	OVERWRITE = ultipa_pb2.OVERWRITE
	UPSERT = ultipa_pb2.UPSERT


class PropertyType:
	PROPERTY_UNSET = ultipa_pb2.UNSET
	PROPERTY_INT32 = ultipa_pb2.INT32
	PROPERTY_STRING = ultipa_pb2.STRING
	PROPERTY_FLOAT = ultipa_pb2.FLOAT
	PROPERTY_DOUBLE = ultipa_pb2.DOUBLE
	PROPERTY_UINT32 = ultipa_pb2.UINT32
	PROPERTY_INT64 = ultipa_pb2.INT64
	PROPERTY_UINT64 = ultipa_pb2.UINT64
	PROPERTY_DATETIME = ultipa_pb2.DATETIME
	PROPERTY_TIMESTAMP = ultipa_pb2.TIMESTAMP
	PROPERTY_TEXT = ultipa_pb2.TEXT
	PROPERTY_BLOB = ultipa_pb2.BLOB
	PROPERTY_POINT = ultipa_pb2.POINT
	PROPERTY_DECIMAL = ultipa_pb2.DECIMAL
	PROPERTY_LIST = ultipa_pb2.LIST
	PROPERTY_SET = ultipa_pb2.SET
	PROPERTY_MAP = ultipa_pb2.MAP
	PROPERTY_NULL = ultipa_pb2.NULL_
	PROPERTY_UUID = -1
	PROPERTY_ID = -2
	PROPERTY_FROM = -3
	PROPERTY_FROM_UUID = -4
	PROPERTY_TO = -5
	PROPERTY_TO_UUID = -6
	PROPERTY_IGNORE = -7


class ResultType:
	RESULT_TYPE_UNSET = ultipa_pb2.RESULT_TYPE_UNSET
	RESULT_TYPE_PATH = ultipa_pb2.RESULT_TYPE_PATH
	RESULT_TYPE_NODE = ultipa_pb2.RESULT_TYPE_NODE
	RESULT_TYPE_EDGE = ultipa_pb2.RESULT_TYPE_EDGE
	RESULT_TYPE_ATTR = ultipa_pb2.RESULT_TYPE_ATTR
	# RESULT_TYPE_ARRAY = ultipa_pb2.RESULT_TYPE_ARRAY
	RESULT_TYPE_TABLE = ultipa_pb2.RESULT_TYPE_TABLE
	RESULT_TYPE_ExplainPlan = "ExplainPlan"

	@staticmethod
	def getTypeStr(type):
		if type == ResultType.RESULT_TYPE_PATH:
			return 'PATH'
		elif type == ResultType.RESULT_TYPE_NODE:
			return 'NODE'
		elif type == ResultType.RESULT_TYPE_EDGE:
			return "EDGE"
		elif type == ResultType.RESULT_TYPE_ATTR:
			return "ATTR"
		elif type == PropertyType.PROPERTY_LIST:
			return "LIST"
		elif type == ResultType.RESULT_TYPE_TABLE:
			return "TABLE"
		elif type == ResultType.RESULT_TYPE_UNSET:
			return "UNSET"
		elif type == ResultType.RESULT_TYPE_ExplainPlan:
			return "EXPLAINPLAN"
		else:
			return type


class Code:
	SUCCESS = ultipa_pb2.SUCCESS
	FAILED = ultipa_pb2.FAILED
	PARAM_ERROR = ultipa_pb2.PARAM_ERROR
	BASE_DB_ERROR = ultipa_pb2.BASE_DB_ERROR
	ENGINE_ERROR = ultipa_pb2.ENGINE_ERROR
	SYSTEM_ERROR = ultipa_pb2.SYSTEM_ERROR
	RAFT_REDIRECT = ultipa_pb2.RAFT_REDIRECT
	RAFT_LEADER_NOT_YET_ELECTED = ultipa_pb2.RAFT_LEADER_NOT_YET_ELECTED
	RAFT_LOG_ERROR = ultipa_pb2.RAFT_LOG_ERROR
	UQL_ERROR = ultipa_pb2.UQL_ERROR
	NOT_RAFT_MODE = ultipa_pb2.NOT_RAFT_MODE
	RAFT_NO_AVAILABLE_FOLLOWERS = ultipa_pb2.RAFT_NO_AVAILABLE_FOLLOWERS
	RAFT_NO_AVAILABLE_ALGO_SERVERS = ultipa_pb2.RAFT_NO_AVAILABLE_ALGO_SERVERS
	PERMISSION_DENIED = ultipa_pb2.PERMISSION_DENIED

	UNKNOW_ERROR = 1000


class FollowerRole:
	ROLE_UNSET = ultipa_pb2.ROLE_UNSET
	ROLE_READABLE = ultipa_pb2.ROLE_READABLE
	ROLE_ALGO_EXECUTABLE = ultipa_pb2.ROLE_ALGO_EXECUTABLE


class ServerStatus:
	DEAD = ultipa_pb2.DEAD
	ALIVE = ultipa_pb2.ALIVE


#
# class PlanNodeType:
# 	CLAUSE_UNSET = ultipa_pb2.CLAUSE_UNSET
# 	ORDER_BY_CLAUSE = ultipa_pb2.ORDER_BY_CLAUSE
# 	AGGREGATION_CLAUSE = ultipa_pb2.AGGREGATION_CLAUSE
# 	WITH_CLAUSE = ultipa_pb2.WITH_CLAUSE
# 	WHERE_CLAUSE = ultipa_pb2.WHERE_CLAUSE
# 	UNCOLLECT_CLAUSE = ultipa_pb2.UNCOLLECT_CLAUSE
# 	TABLE_CLAUSE = ultipa_pb2.TABLE_CLAUSE
# 	RETURN_CLAUSE = ultipa_pb2.RETURN_CLAUSE
# 	LIMIT_SKIP_CLAUSE = ultipa_pb2.LIMIT_SKIP_CLAUSE
# 	TEMPLATE_CLAUSE = ultipa_pb2.TEMPLATE_CLAUSE
# 	KHOP_TEMPLATE_CLAUSE = ultipa_pb2.KHOP_TEMPLATE_CLAUSE
# 	KHOP_CLAUSE = ultipa_pb2.KHOP_CLAUSE
# 	AB_CLAUSE = ultipa_pb2.AB_CLAUSE
# 	SPREAD_CLAUSE = ultipa_pb2.SPREAD_CLAUSE
# 	AUTO_NET_CLAUSE = ultipa_pb2.AUTO_NET_CLAUSE
# 	NODE_SEARCH_CLAUSE = ultipa_pb2.NODE_SEARCH_CLAUSE
# 	EDGE_SEARCH_CLAUSE = ultipa_pb2.EDGE_SEARCH_CLAUSE
# 	NODE_INSERT_CLAUSE = ultipa_pb2.NODE_INSERT_CLAUSE
# 	EDGE_INSERT_CLAUSE = ultipa_pb2.EDGE_INSERT_CLAUSE
# 	NODE_UPSERT_CLAUSE = ultipa_pb2.NODE_UPSERT_CLAUSE
# 	EDGE_UPSERT_CLAUSE = ultipa_pb2.EDGE_UPSERT_CLAUSE
# 	NODE_UPDATE_CLAUSE = ultipa_pb2.NODE_UPDATE_CLAUSE
# 	EDGE_UPDATE_CLAUSE = ultipa_pb2.EDGE_UPDATE_CLAUSE
# 	NODE_DELETE_CLAUSE = ultipa_pb2.NODE_DELETE_CLAUSE
# 	EDGE_DELETE_CLAUSE = ultipa_pb2.EDGE_DELETE_CLAUSE
# 	TRUNCATE_CLAUSE = ultipa_pb2.TRUNCATE_CLAUSE
# 	COMPACT_CLAUSE = ultipa_pb2.COMPACT_CLAUSE
# 	GRAPH_CREATE_CLAUSE = ultipa_pb2.GRAPH_CREATE_CLAUSE
# 	GRAPH_DROP_CLAUSE = ultipa_pb2.GRAPH_DROP_CLAUSE
# 	GRAPH_UPDATE_CLAUSE = ultipa_pb2.GRAPH_UPDATE_CLAUSE
# 	GRAPH_SHOW_CLAUSE = ultipa_pb2.GRAPH_SHOW_CLAUSE
# 	GRAPH_MOUNT_CLAUSE = ultipa_pb2.GRAPH_MOUNT_CLAUSE
# 	GRAPH_UNMOUNT_CLAUSE = ultipa_pb2.GRAPH_UNMOUNT_CLAUSE
# 	SCHEMA_CREATE_CLAUSE = ultipa_pb2.SCHEMA_CREATE_CLAUSE
# 	SCHEMA_DROP_CLAUSE = ultipa_pb2.SCHEMA_DROP_CLAUSE
# 	SCHEMA_ALTER_CLAUSE = ultipa_pb2.SCHEMA_ALTER_CLAUSE
# 	SCHEMA_SHOW_CLAUSE = ultipa_pb2.SCHEMA_SHOW_CLAUSE
# 	PROPERTY_CREATE_CLAUSE = ultipa_pb2.PROPERTY_CREATE_CLAUSE
# 	PROPERTY_DROP_CLAUSE = ultipa_pb2.PROPERTY_DROP_CLAUSE
# 	PROPERTY_ALTER_CLAUSE = ultipa_pb2.PROPERTY_ALTER_CLAUSE
# 	PROPERTY_SHOW_CLAUSE = ultipa_pb2.PROPERTY_SHOW_CLAUSE
# 	FULLTEXT_CREATE_CLAUSE = ultipa_pb2.FULLTEXT_CREATE_CLAUSE
# 	FULLTEXT_DROP_CLAUSE = ultipa_pb2.FULLTEXT_DROP_CLAUSE
# 	FULLTEXT_SHOW_CLAUSE = ultipa_pb2.FULLTEXT_SHOW_CLAUSE
# 	INDEX_CREATE_CLAUSE = ultipa_pb2.INDEX_CREATE_CLAUSE
# 	INDEX_DROP_CLAUSE = ultipa_pb2.INDEX_DROP_CLAUSE
# 	INDEX_SHOW_CLAUSE = ultipa_pb2.INDEX_SHOW_CLAUSE
# 	LTE_CLAUSE = ultipa_pb2.LTE_CLAUSE
# 	UFE_CLAUSE = ultipa_pb2.UFE_CLAUSE
# 	TASK_CLEAR_CLAUSE = ultipa_pb2.TASK_CLEAR_CLAUSE
# 	TASK_STOP_CLAUSE = ultipa_pb2.TASK_STOP_CLAUSE
# 	TASK_PAUSE_CLAUSE = ultipa_pb2.TASK_PAUSE_CLAUSE
# 	TASK_RESUME_CLAUSE = ultipa_pb2.TASK_RESUME_CLAUSE
# 	TASK_SHOW_CLAUSE = ultipa_pb2.TASK_SHOW_CLAUSE
# 	TOP_CLAUSE = ultipa_pb2.TOP_CLAUSE
# 	KILL_CLAUSE = ultipa_pb2.KILL_CLAUSE
# 	STAT_CLAUSE = ultipa_pb2.STAT_CLAUSE
# 	POLICY_SHOW_CLAUSE = ultipa_pb2.POLICY_SHOW_CLAUSE
# 	POLICY_CREATE_CLAUSE = ultipa_pb2.POLICY_CREATE_CLAUSE
# 	POLICY_DELETE_CLAUSE = ultipa_pb2.POLICY_DELETE_CLAUSE
# 	POLICY_UPDATE_CLAUSE = ultipa_pb2.POLICY_UPDATE_CLAUSE
# 	USER_SHOW_CLAUSE = ultipa_pb2.USER_SHOW_CLAUSE
# 	USER_CREATE_CLAUSE = ultipa_pb2.USER_CREATE_CLAUSE
# 	USER_DELETE_CLAUSE = ultipa_pb2.USER_DELETE_CLAUSE
# 	USER_UPDATE_CLAUSE = ultipa_pb2.USER_UPDATE_CLAUSE
# 	PRIVILEGE_SHOW_CLAUSE = ultipa_pb2.PRIVILEGE_SHOW_CLAUSE
# 	GRANT_CLAUSE = ultipa_pb2.GRANT_CLAUSE
# 	REVOKE_CLAUSE = ultipa_pb2.REVOKE_CLAUSE
# 	SELF_INFO_GET_CLAUSE = ultipa_pb2.SELF_INFO_GET_CLAUSE
# 	ALGO_CLAUSE = ultipa_pb2.ALGO_CLAUSE
# 	ALGO_WRITE_CLAUSE = ultipa_pb2.ALGO_WRITE_CLAUSE
# 	ALGO_LIST_CLAUSE = ultipa_pb2.ALGO_LIST_CLAUSE
# 	SUB_GRAPH_CLAUSE = ultipa_pb2.SUB_GRAPH_CLAUSE
# 	OPTIONAL_TEMPLATE_CLAUSE = ultipa_pb2.OPTIONAL_TEMPLATE_CLAUSE
# 	SUBQUERY_CLAUSE = ultipa_pb2.SUBQUERY_CLAUSE
# 	UNION_CLAUSE = ultipa_pb2.UNION_CLAUSE
#
# 	@staticmethod
# 	def getTypeStr(type):
# 		if type == PlanNodeType.CLAUSE_UNSET:
# 			return 'CLAUSE_UNSET'
# 		elif type == PlanNodeType.ORDER_BY_CLAUSE:
# 			return 'ORDER_BY_CLAUSE'
# 		elif type == PlanNodeType.AGGREGATION_CLAUSE:
# 			return "AGGREGATION_CLAUSE"
# 		elif type == PlanNodeType.WITH_CLAUSE:
# 			return "WITH_CLAUSE"
# 		elif type == PlanNodeType.WHERE_CLAUSE:
# 			return "WHERE_CLAUSE"
# 		elif type == PlanNodeType.UNCOLLECT_CLAUSE:
# 			return "UNCOLLECT_CLAUSE"
# 		elif type == PlanNodeType.TABLE_CLAUSE:
# 			return "TABLE_CLAUSE"
# 		elif type == PlanNodeType.RETURN_CLAUSE:
# 			return "RETURN_CLAUSE"
# 		elif type == PlanNodeType.LIMIT_SKIP_CLAUSE:
# 			return "LIMIT_SKIP_CLAUSE"
# 		elif type == PlanNodeType.TEMPLATE_CLAUSE:
# 			return "TEMPLATE_CLAUSE"
# 		elif type == PlanNodeType.KHOP_TEMPLATE_CLAUSE:
# 			return "KHOP_TEMPLATE_CLAUSE"
# 		elif type == PlanNodeType.KHOP_CLAUSE:
# 			return 'KHOP_CLAUSE'
# 		elif type == PlanNodeType.AB_CLAUSE:
# 			return "AB_CLAUSE"
# 		elif type == PlanNodeType.SPREAD_CLAUSE:
# 			return "SPREAD_CLAUSE"
# 		elif type == PlanNodeType.AUTO_NET_CLAUSE:
# 			return "AUTO_NET_CLAUSE"
# 		elif type == PlanNodeType.NODE_SEARCH_CLAUSE:
# 			return "NODE_SEARCH_CLAUSE"
# 		elif type == PlanNodeType.NODE_INSERT_CLAUSE:
# 			return "NODE_INSERT_CLAUSE"
# 		elif type == PlanNodeType.NODE_UPSERT_CLAUSE:
# 			return "NODE_UPSERT_CLAUSE"
# 		elif type == PlanNodeType.NODE_UPDATE_CLAUSE:
# 			return "NODE_UPDATE_CLAUSE"
# 		elif type == PlanNodeType.NODE_DELETE_CLAUSE:
# 			return "NODE_DELETE_CLAUSE"
# 		elif type == PlanNodeType.EDGE_SEARCH_CLAUSE:
# 			return "EDGE_SEARCH_CLAUSE"
# 		elif type == PlanNodeType.EDGE_INSERT_CLAUSE:
# 			return 'EDGE_INSERT_CLAUSE'
# 		elif type == PlanNodeType.EDGE_UPSERT_CLAUSE:
# 			return "EDGE_UPSERT_CLAUSE"
# 		elif type == PlanNodeType.EDGE_UPDATE_CLAUSE:
# 			return "EDGE_UPDATE_CLAUSE"
# 		elif type == PlanNodeType.EDGE_DELETE_CLAUSE:
# 			return "EDGE_DELETE_CLAUSE"
# 		elif type == PlanNodeType.TRUNCATE_CLAUSE:
# 			return "TRUNCATE_CLAUSE"
# 		elif type == PlanNodeType.COMPACT_CLAUSE:
# 			return "COMPACT_CLAUSE"
# 		elif type == PlanNodeType.GRAPH_SHOW_CLAUSE:
# 			return "GRAPH_SHOW_CLAUSE"
# 		elif type == PlanNodeType.GRAPH_CREATE_CLAUSE:
# 			return "GRAPH_CREATE_CLAUSE"
# 		elif type == PlanNodeType.GRAPH_DROP_CLAUSE:
# 			return "GRAPH_DROP_CLAUSE"
# 		elif type == PlanNodeType.GRAPH_UPDATE_CLAUSE:
# 			return "GRAPH_UPDATE_CLAUSE"
# 		elif type == PlanNodeType.GRAPH_MOUNT_CLAUSE:
# 			return 'GRAPH_MOUNT_CLAUSE'
# 		elif type == PlanNodeType.GRAPH_UNMOUNT_CLAUSE:
# 			return "GRAPH_UNMOUNT_CLAUSE"
# 		elif type == PlanNodeType.SCHEMA_CREATE_CLAUSE:
# 			return "SCHEMA_CREATE_CLAUSE"
# 		elif type == PlanNodeType.SCHEMA_DROP_CLAUSE:
# 			return "SCHEMA_DROP_CLAUSE"
# 		elif type == PlanNodeType.SCHEMA_ALTER_CLAUSE:
# 			return "SCHEMA_ALTER_CLAUSE"
# 		elif type == PlanNodeType.SCHEMA_SHOW_CLAUSE:
# 			return "SCHEMA_SHOW_CLAUSE"
# 		elif type == PlanNodeType.PROPERTY_CREATE_CLAUSE:
# 			return "PROPERTY_CREATE_CLAUSE"
# 		elif type == PlanNodeType.PROPERTY_DROP_CLAUSE:
# 			return "PROPERTY_DROP_CLAUSE"
# 		elif type == PlanNodeType.PROPERTY_ALTER_CLAUSE:
# 			return "PROPERTY_ALTER_CLAUSE"
# 		elif type == PlanNodeType.PROPERTY_SHOW_CLAUSE:
# 			return "PROPERTY_SHOW_CLAUSE"
# 		elif type == PlanNodeType.FULLTEXT_CREATE_CLAUSE:
# 			return 'FULLTEXT_CREATE_CLAUSE'
# 		elif type == PlanNodeType.FULLTEXT_DROP_CLAUSE:
# 			return "FULLTEXT_DROP_CLAUSE"
# 		elif type == PlanNodeType.FULLTEXT_SHOW_CLAUSE:
# 			return "FULLTEXT_SHOW_CLAUSE"
# 		elif type == PlanNodeType.INDEX_CREATE_CLAUSE:
# 			return "INDEX_CREATE_CLAUSE"
# 		elif type == PlanNodeType.INDEX_DROP_CLAUSE:
# 			return "INDEX_DROP_CLAUSE"
# 		elif type == PlanNodeType.INDEX_SHOW_CLAUSE:
# 			return "INDEX_SHOW_CLAUSE"
# 		elif type == PlanNodeType.LTE_CLAUSE:
# 			return "LTE_CLAUSE"
# 		elif type == PlanNodeType.UFE_CLAUSE:
# 			return "UFE_CLAUSE"
# 		elif type == PlanNodeType.TASK_CLEAR_CLAUSE:
# 			return "TASK_CLEAR_CLAUSE"
# 		elif type == PlanNodeType.TASK_STOP_CLAUSE:
# 			return "TASK_STOP_CLAUSE"
# 		elif type == PlanNodeType.TASK_PAUSE_CLAUSE:
# 			return 'TASK_PAUSE_CLAUSE'
# 		elif type == PlanNodeType.TASK_RESUME_CLAUSE:
# 			return "TASK_RESUME_CLAUSE"
# 		elif type == PlanNodeType.TASK_SHOW_CLAUSE:
# 			return "TASK_SHOW_CLAUSE"
# 		elif type == PlanNodeType.TOP_CLAUSE:
# 			return "TOP_CLAUSE"
# 		elif type == PlanNodeType.KILL_CLAUSE:
# 			return "KILL_CLAUSE"
# 		elif type == PlanNodeType.STAT_CLAUSE:
# 			return "STAT_CLAUSE"
# 		elif type == PlanNodeType.POLICY_SHOW_CLAUSE:
# 			return "POLICY_SHOW_CLAUSE"
# 		elif type == PlanNodeType.POLICY_CREATE_CLAUSE:
# 			return "POLICY_CREATE_CLAUSE"
# 		elif type == PlanNodeType.POLICY_DELETE_CLAUSE:
# 			return "POLICY_DELETE_CLAUSE"
# 		elif type == PlanNodeType.POLICY_UPDATE_CLAUSE:
# 			return "POLICY_UPDATE_CLAUSE"
# 		elif type == PlanNodeType.USER_SHOW_CLAUSE:
# 			return 'USER_SHOW_CLAUSE'
# 		elif type == PlanNodeType.USER_CREATE_CLAUSE:
# 			return "USER_CREATE_CLAUSE"
# 		elif type == PlanNodeType.USER_DELETE_CLAUSE:
# 			return "USER_DELETE_CLAUSE"
# 		elif type == PlanNodeType.USER_UPDATE_CLAUSE:
# 			return "USER_UPDATE_CLAUSE"
# 		elif type == PlanNodeType.PRIVILEGE_SHOW_CLAUSE:
# 			return "PRIVILEGE_SHOW_CLAUSE"
# 		elif type == PlanNodeType.GRANT_CLAUSE:
# 			return "GRANT_CLAUSE"
# 		elif type == PlanNodeType.REVOKE_CLAUSE:
# 			return "REVOKE_CLAUSE"
# 		elif type == PlanNodeType.SELF_INFO_GET_CLAUSE:
# 			return "SELF_INFO_GET_CLAUSE"
# 		elif type == PlanNodeType.ALGO_CLAUSE:
# 			return "ALGO_CLAUSE"
# 		elif type == PlanNodeType.ALGO_WRITE_CLAUSE:
# 			return "ALGO_WRITE_CLAUSE"
# 		elif type == PlanNodeType.ALGO_LIST_CLAUSE:
# 			return 'ALGO_LIST_CLAUSE'
# 		elif type == PlanNodeType.SUB_GRAPH_CLAUSE:
# 			return "SUB_GRAPH_CLAUSE"
# 		elif type == PlanNodeType.OPTIONAL_TEMPLATE_CLAUSE:
# 			return "OPTIONAL_TEMPLATE_CLAUSE"
# 		elif type == PlanNodeType.SUBQUERY_CLAUSE:
# 			return "SUBQUERY_CLAUSE"
# 		elif type == PlanNodeType.UNION_CLAUSE:
# 			return "UNION_CLAUSE"
# 		else:
# 			return type


class SchemaProperty:
	'''
	Schema properties
	'''

	name: str
	type: str
	description: str
	lte: str


# class SchemaValue:
#     def __init__(self,description,schemaName,properties:List[Property],totalNodes):
#         self.description=description
#         self.properties=properties
#         self.schemaName=schemaName
#         self.totalNodes=totalNodes

class Schema:

	def __init__(self, description: str, schemaName: str, properties: List[SchemaProperty], total: int, type: str):
		self.description = description
		self.properties = properties
		self.name = schemaName
		self.total = total
		self.type = type


# class OPTION:
#     OPT_GET=ultipa_pb2.OPT_GET
#     OPT_SET=ultipa_pb2.OPTION.OPT_SET

class RaftPeerInfo:
	def __init__(self, host, status=None, isLeader=False, isAlgoExecutable=False, isFollowerReadable=False,
				 isUnset=False):
		self.host = host
		self.status = status
		self.isLeader = isLeader
		self.isAlgoExecutable = isAlgoExecutable
		self.isFollowerReadable = isFollowerReadable
		self.isUnset = isUnset


class ClusterInfo:
	def __init__(self, redirect: str, raftPeers: List[RaftPeerInfo], leader: RaftPeerInfo = None):
		self.redirect = redirect
		self.leader = leader
		self.raftPeers = raftPeers


class Status:
	def __init__(self, code: Code, message: str, clusterInfo: ClusterInfo = None):
		self.code = code
		self.message = message.strip('\n')
		if clusterInfo:
			self.clusterInfo = clusterInfo


class BaseModel:

	def toJSON(self, pretty=False):
		try:
			if pretty:
				return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)
			else:
				return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, ensure_ascii=False)
		except Exception as e:
			return self

	def toDict(self) -> Dict:
		return json.loads(self.toJSON())

	def __str__(self):
		return str(self.__dict__)


class UQLSchema(BaseModel):

	def __init__(self, description: str, schemaName: str, properties: List[SchemaProperty], total: int, type: str):
		self.description = description
		self.properties = properties
		self.name = schemaName
		self.total = total
		self.type = type


class UQLProperty(BaseModel):
	lte: bool
	name: str
	type: str
	description: str
	schema: str


class UQLGraph(BaseModel):
	id: str
	name: str
	totalNodes: str
	totalEdges: str
	description: str
	status: str


class UQLAlgos(BaseModel):
	name: str
	description: str
	version: str
	result_opt: str
	parameters: dict
	write_to_stats_parameters: dict
	write_to_db_parameters: dict
	write_to_file_parameters: dict


class Node(BaseModel):
	_index = None

	def __init__(self, values: Dict, schema: str = None, id: str = None, uuid: int = None, **kwargs):
		self.id = id
		if schema is None:
			if kwargs.get("schema_name") is not None:
				self.schema = kwargs.get("schema_name")
			else:
				self.schema = None
		else:
			self.schema = schema
		self.values = values
		self.uuid = uuid

	def getID(self):
		return self.id

	def getUUID(self):
		return self.uuid

	def getValues(self):
		return self.values

	def getSchema(self):
		return self.schema

	def get(self, propertyName: str):
		return self.values.get(propertyName)

	def set(self, propertyName: str, value):
		self.values.update({propertyName: value})

	def _getIndex(self):
		return self._index


class Edge(BaseModel):
	_index = None

	def __init__(self, values: Dict, from_id: str = None, from_uuid: int = None, to_id: str = None, to_uuid: int = None,
				 schema: str = None,
				 uuid: int = None, **kwargs):
		if schema is None:
			if kwargs.get("schema_name") is not None:
				self.schema = kwargs.get("schema_name")
			else:
				self.schema = None
		else:
			self.schema = schema

		self.from_id = from_id
		self.from_uuid = from_uuid
		self.to_id = to_id
		self.to_uuid = to_uuid
		self.values = values
		self.uuid = uuid

	def getUUID(self):
		return self.uuid

	def getFrom(self):
		return self.from_id

	def getTo(self):
		return self.to_id

	def getFromUUID(self):
		return self.from_uuid

	def getToUUID(self):
		return self.to_uuid

	def getValues(self):
		return self.values

	def getSchema(self):
		return self.schema

	def get(self, propertyName: str):
		return self.values.get(propertyName)

	def set(self, propertyName: str, value):
		self.values.update({propertyName: value})

	def _getIndex(self):
		return self._index


class EntityRow:
	_index = None

	def __init__(self, values: Dict, schema: str = None, id: str = None, from_id: str = None, to_id: str = None,
				 uuid: int = None, from_uuid: int = None, to_uuid: int = None, **kwargs):
		self.uuid = uuid
		self.id = id
		self.from_uuid = from_uuid
		self.to_uuid = to_uuid
		self.from_id = from_id
		self.to_id = to_id
		if schema is None:
			if kwargs.get("schema_name") is not None:
				self.schema = kwargs.get("schema_name")
			else:
				self.schema = None
		else:
			self.schema = schema
		self.values = values

	def _getIndex(self):
		return self._index


class Path(BaseModel):
	nodeSchemas: Dict[str, Schema] = {}
	edgeSchemas: Dict[str, Schema] = {}

	def __init__(self, nodes: List[Node], edges: List[Edge], nodeSchemas, edgeSchemas):
		self.nodes = nodes
		self.edges = edges
		self.nodeSchemas = nodeSchemas
		self.edgeSchemas = edgeSchemas

	# for node in nodes:
	#     if node.schema not in self.nodeSchemas:
	#         self.nodeSchemas.append(node.schema)
	#
	# for edge in edges:
	#     if edge.schema not in self.edgeSchemas:
	#         self.edgeSchemas.append(edge.schema)

	def length(self):
		return len(self.edges)

	def getNodes(self):
		return self.nodes

	def getEdges(self):
		return self.edges


class PathAlias:
	def __init__(self, alias: str, paths: List[Path] = None):
		self.alias = alias
		if paths is None:
			paths = []
		self.paths = paths

	def length(self):
		return len(self.paths)

	def getNodes(self):
		nodes = [i.nodes for i in self.paths]
		return nodes

	def getEdges(self):
		edges = [i.edges for i in self.paths]
		return edges


class NodeAlias:
	def __init__(self, alias: str, nodes: List[Node] = None):
		self.alias = alias
		if nodes is None:
			nodes = []
		self.nodes = nodes


class Header:
	property_type: str
	property_name: str


class SchemaHeader:
	schema_name: str
	headers: List[Header]


class NodeTable:
	def __init__(self, schemas: List[object], nodeRows: List[Node] = None):
		# newHeaderList = [{"schema_name": schema_name, "properties":[{"property_name":"","property_type(PropertyType)":""}]}]
		# nodeRowsList = [{"schema_name": schema_name, 'values': [values]}]
		self.schemas = schemas
		if nodeRows is None:
			nodeRows = []
		self.nodeRows = nodeRows

	def __del__(self):
		pass


class NodeEntityTable:
	def __init__(self, schemas: List[object], nodeRows: List[EntityRow] = None):
		self.schemas = schemas
		if nodeRows is None:
			nodeRows = []
		self.nodeRows = nodeRows

	def __del__(self):
		pass


class EdgeTable:
	def __init__(self, schemas: List[object], edgeRows: List[Edge] = None):
		self.schemas = schemas
		if edgeRows is None:
			edgeRows = []
		self.edgeRows = edgeRows


class EdgeEntityTable:
	def __init__(self, schemas: List[object], edgeRows: List[EntityRow] = None):
		self.schemas = schemas
		if edgeRows is None:
			edgeRows = []
		self.edgeRows = edgeRows

	def __del__(self):
		pass


class EntityTable:
	def __init__(self, schemas: List[object], entity_rows: List[EntityRow] = None):
		# newHeaderList = [{"schema_name": schema_name, "properties":[{"property_name":"","property_type(PropertyType)":""}]}]
		# nodeRowsList = [{"schema_name": schema_name, 'values': [values]}]
		self.schemas = schemas
		if entity_rows is None:
			entity_rows = []
		self.entity_rows = entity_rows

	def __del__(self):
		pass


class EdgeAlias:
	def __init__(self, alias: str, edges: List[Edge]):
		self.alias = alias
		self.edges = edges





class AttrAlias:
	def __init__(self, alias: str, values: any, type: ResultType = None,type_desc:str=None):
		self.name = alias
		self.values = values
		self.type = type
		self.type_desc = type_desc

class AttrNodeAlias:
	def __init__(self, alias: str, values:  List[List[Node]], type: ResultType = None,type_desc:str=None):
		self.name = alias
		self.values = values
		self.type = type
		self.type_desc = type_desc

class AttrEdgeAlias:
	def __init__(self, alias: str, values: List[List[Edge]], type: ResultType = None,type_desc:str=None):
		self.name = alias
		self.values = values
		self.type = type
		self.type_desc = type_desc

class AttrPathAlias:
	def __init__(self, alias: str, values: List[List[Path]], type: ResultType = None,type_desc:str=None):
		self.name = alias
		self.values = values
		self.type = type
		self.type_desc = type_desc

class Attr:

	def __init__(self, type: PropertyType, values: any,has_attr_data:bool=False,has_ultipa_data:bool=False,type_desc: any = None):
		self.values = values
		self.type = type
		self.type_desc = type_desc
		self.has_attr_data = has_attr_data
		self.has_ultipa_data = has_ultipa_data


class AttrNewAlias:
	def __init__(self, alias: str, attr: Attr):
		self.alias = alias
		self.attr = attr



class ResultAlias:
	def __init__(self, alias: str, result_type: int):
		self.alias = alias
		self.result_type = result_type


class Table(BaseModel):
	def __init__(self, table_name: str, headers: List[dict], table_rows: List[List]):
		self.name = table_name
		self.rows = table_rows
		self.headers = headers

	def getHeaders(self):
		return self.headers

	def getRows(self):
		return self.rows

	def getName(self):
		return self.name


# class Tables(BaseModel):
#     def __init__(self, table_name: str, table_rows: List[Dict]):
#         self.table_name = table_name
#         self.table_rows = table_rows
#
#     def toKV(self):
#         return self.toDict()
#
#     def getHeaders(self):
#         return self.table_name
#
#     def getRows(self):
#         return self.table_rows


class Values:
	def __init__(self, key: str, value: str):
		self.key = key
		self.value = value


class ArrayAlias:
	def __init__(self, alias: str, elements):
		self.alias = alias
		self.elements = elements


class ExplainPlan:
	def __init__(self, alias, childrenNum, uql, infos):
		# self.type = type
		self.alias = alias
		self.children_num = childrenNum
		self.uql = uql
		self.infos = infos
		self.id = str(uuid.uuid4())


class DataItem(BaseModel):

	def __init__(self, alias: str, data: any, type: str):
		self.alias = alias
		self.data = data
		self.type = type

	def asNodes(self) -> List[Node]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
			error = f"DataItem {self.alias} is not Type Node"
			raise ParameterException(error)
		return self.data

	def asFirstNodes(self) -> Node:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
			error = f"DataItem {self.alias} is not Type Node"
			raise ParameterException(error)
		return self.data[0] if len(self.data) > 0 else None

	def asEdges(self) -> List[Edge]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
			error = f"DataItem {self.alias} is not Type Edge"
			raise ParameterException(error)
		return self.data

	def asFirstEdges(self) -> Edge:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
			error = f"DataItem {self.alias} is not Type Edge"
			raise ParameterException(error)
		return self.data[0] if len(self.data) > 0 else None

	def asPaths(self) -> List[Path]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH):
			error = f"DataItem {self.alias} is not Type Path"
			raise ParameterException(error)
		return self.data

	def asAttr(self) -> AttrAlias:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR):
			error = f"DataItem {self.alias} is not Type Attribute list"
			raise ParameterException(error)

		return self.data

	def asNodeList(self) -> AttrNodeAlias:
		return self.asAttr()

	def asEdgeList(self) -> AttrEdgeAlias:
		return self.asAttr()

	def asPathList(self) -> AttrPathAlias:
		return self.asAttr()


	def asTable(self) -> Table:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
			error = f"DataItem {self.alias} is not Type Table"
			raise ParameterException(error)
		return self.data

	def asArray(self) -> ArrayAlias:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return None
			return self.data
		# if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_ARRAY):
		# 	error = f"DataItem {self.alias} is not Type Array"
		# 	raise ParameterException(error)
		return self.data

	def asSchemas(self) -> List[UQLSchema]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
			error = f"DataItem {self.alias} is not Type Table"
			raise ParameterException(error)
		alias = self.data.getName()
		headers = self.data.getHeaders()
		rows = self.data.getRows()
		tableListDict = convertTableToDict(rows, headers)
		REPLACE_KEYS = {
			"totalNodes": "total",
			"totalEdges": "total",
		}
		BOOL_KEYS = ["index", "lte"]
		JSON_KEYS = ["properties"]
		convert2Int = ["totalNodes", "totalEdges"]
		responseKeyFormat = ResponseKeyFormat(keyReplace=REPLACE_KEYS, boolKeys=BOOL_KEYS, jsonKeys=JSON_KEYS,
											  convert2Int=convert2Int)
		if alias == "_nodeSchema":
			for data in tableListDict:
				data.update({"type": "Node"})
		elif alias == "_edgeSchema":
			for data in tableListDict:
				data.update({"type": "Edge"})
		data = responseKeyFormat.changeKeyValue(tableListDict)
		data = convertToListAnyObject(data)
		return data

	def asProperties(self) -> List[UQLProperty]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
			error = f"DataItem {self.alias} is not Type Table"
			raise ParameterException(error)
		headers = self.data.getHeaders()
		rows = self.data.getRows()
		table_rows_dict = convertTableToDict(rows, headers)
		BOOL_KEYS = ["lte"]
		responseKeyFormat = ResponseKeyFormat(boolKeys=BOOL_KEYS)
		data = responseKeyFormat.changeKeyValue(table_rows_dict)
		data = convertToListAnyObject(data)
		return data

	def asGraphs(self) -> List[UQLGraph]:
		REPLACE_KEYS = {
			"graph": "name",
		}
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
			error = f"DataItem {self.alias} is not Type Table"
			raise ParameterException(error)
		headers = self.data.getHeaders()
		rows = self.data.getRows()
		table_rows_dict = convertTableToDict(rows, headers)
		responseKeyFormat = ResponseKeyFormat(keyReplace=REPLACE_KEYS)
		data = responseKeyFormat.changeKeyValue(table_rows_dict)
		data = convertToListAnyObject(data)
		return data

	def asAlgos(self) -> List[UQLAlgos]:
		if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
			if self.data is None:
				return []
			return self.data
		if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
			error = f"DataItem {self.alias} is not Type Table"
			raise ParameterException(error)
		headers = self.data.getHeaders()
		rows = self.data.getRows()
		table_rows_dict = convertTableToDict(rows, headers)
		algo_list = []
		for data in table_rows_dict:
			algo_list.append(json.loads(data.get("param")))

		responseKeyFormat = ResponseKeyFormat()
		data = responseKeyFormat.changeKeyValue(algo_list)
		data = convertAlgoList2AnyObject(data)

		return data

	# def asExplainPlan(self) -> List[ExplainPlan]:
	# 	return self.data

	def asAny(self) -> any:
		return self.data

	def asKV(self):
		return self.toDict()


class BaseUqlReply:
	def __init__(self, paths: List[PathAlias], nodes: List[NodeAlias], edges: List[EdgeAlias], tables: List[Table],
				 attrs: List = None, resultAlias: List = None,
				 explainPlan: List[ExplainPlan] = None):
		self.paths = paths
		self.nodes = nodes
		self.edges = edges
		self.tables = tables
		self.attrs = attrs
		# self.arrays = arrays
		self.resultAlias = resultAlias
		self.explainPlan = explainPlan


class UltipaStatistics(BaseModel):
	def __init__(self, edge_affected: int, node_affected: int, engine_time_cost: int, total_time_cost: int):
		self.edgeAffected = edge_affected
		self.nodeAffected = node_affected
		self.engineCost = engine_time_cost
		self.totalCost = total_time_cost


class UqlReply(BaseModel):
	datas: List[DataItem]

	def __init__(self, dataBase: BaseUqlReply, aliasMap: dict = None, datas: List = None):
		if aliasMap == None:
			aliasMap = {}
		self._aliasMap = aliasMap
		if datas is None:
			datas = []
		self.datas: List[DataItem] = datas
		self.explainPlan: List[ExplainPlan] = []
		self._dataBase = dataBase
		# self.total_time_cost = total_time_cost
		# self.engine_time_cost = engine_time_cost

		for data in self._dataBase.paths:
			if self._aliasMap.get(data.alias):
				self._aliasMap[data.alias].data.extend(data.paths)
				continue
			self._aliasMap[data.alias] = DataItem(data.alias, data.paths,
												  ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH))

		for data in self._dataBase.nodes:
			if self._aliasMap.get(data.alias):
				self._aliasMap[data.alias].data.extend(data.nodes)
				continue
			self._aliasMap[data.alias] = DataItem(data.alias, data.nodes,
												  ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE))

		for data in self._dataBase.edges:
			if self._aliasMap.get(data.alias):
				self._aliasMap[data.alias].data.extend(data.edges)
				continue
			self._aliasMap[data.alias] = DataItem(data.alias, data.edges,
												  ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE))

		for data in self._dataBase.attrs:
			if self._aliasMap.get(data.name):
				self._aliasMap[data.name].data.append(data)
				continue
			self._aliasMap[data.name] = DataItem(data.name, data, ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR))
			# if data.type in ["list"]:
			# 	for attrRow in data.rows:
			# 		if attrRow.type == ResultType.RESULT_TYPE_NODE:
			# 			if attrRow.nodes and len(attrRow.nodes)>0:
			# 				if self._aliasMap.get(data.name):
			# 					self._aliasMap[data.name].data.extend(attrRow.nodes)
			# 				else:
			# 					self._aliasMap[data.name] = DataItem(data.name, attrRow.nodes,
			# 														 ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE))
			# 		elif attrRow.type == ResultType.RESULT_TYPE_EDGE:
			# 			if attrRow.edges and len(attrRow.edges)>0:
			# 				if self._aliasMap.get(data.name):
			# 					self._aliasMap[data.name].data.extend(attrRow.nodes)
			# 				else:
			# 					self._aliasMap[data.name] = DataItem(data.name, attrRow.edges,
			# 														 ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE))
			# 		elif attrRow.type == ResultType.RESULT_TYPE_PATH:
			# 			if attrRow.paths and len(attrRow.paths)>0:
			# 				if self._aliasMap.get(data.name):
			# 					self._aliasMap[data.name].data.extend(attrRow.paths)
			# 				else:
			# 					self._aliasMap[data.name] = DataItem(data.name, attrRow.paths,
			# 														 ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH))
			# 		else:
			# 			if attrRow.attrs and len(attrRow.attrs) > 0:
			# 				self._aliasMap[data.name] = DataItem(data.name, data,
			# 													 ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR))
			# else:
			# 	self._aliasMap[data.name] = DataItem(data.name, data,
			# 										 ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR))

		# for data in self._dataBase.arrays:
		# 	if self._aliasMap.get(data.alias):
		# 		self._aliasMap[data.alias].data.extend(data)
		# 		continue
		# 	self._aliasMap[data.alias] = DataItem(data.alias, data,
		# 										  ResultType.getTypeStr(ResultType.RESULT_TYPE_ARRAY))

		for data in self._dataBase.tables:
			if self._aliasMap.get(data.name):
				self._aliasMap[data.name].data.extend(data)
				continue
			self._aliasMap[data.name] = DataItem(data.name, data, ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE))

		for data in self._dataBase.explainPlan:
			# if self._aliasMap.get(data.alias):
			#     self._aliasMap[data.alias].data.extend(data)
			#     continue
			self.explainPlan.append(data)

		for data in self._dataBase.resultAlias:
			if self._aliasMap.get(data.alias):
				self.datas.append(self._aliasMap[data.alias])
		if not self.datas:
			for key in self._aliasMap:
				self.datas.append(self._aliasMap[key])


# del self._aliasMap
# del self._dataBase


class Retry:
	def __init__(self, canRetry, currentRetry, nextRetry):
		self.canRetry = canRetry
		self.currentRetry = currentRetry
		self.nextRetry = nextRetry


class ReturnReq:
	def __init__(self, graphSetName: str, uql: str, host: str, retry: Retry, uqlIsExtra: bool):
		self.graph_name = graphSetName
		self.uql = uql
		self.host = host
		self.Retry = retry
		self.uqlIsExtra = uqlIsExtra


# class UltipaResponse(BaseModel):
#     def __init__(self, status: Status = None, total_time: int = 0, engine_time: int = 0, data: List[DataItem] = None,
#                  req:ReturnReq=None,statistics:UltipaStatistics=None):
#         self.status = status
#         self.data = data
#         self.total_time = total_time
#         self.engine_time = engine_time
#         self.req = req
#         self.statistics = statistics
#
#     def alias(self,alias:str) -> DataItem:
#         for data in self.data:
#             if alias == data.alias:
#                 return data
#         return DataItem(alias,None,None)
#
#     def get(self,index:int) -> DataItem:
#         if len(self.data)-1 >= index:
#             return self.data[index]
#         return DataItem(None,None,None)
#
#
#
# class SchemaResponse(BaseModel):
#     def __init__(self, status: Status = None, total_time: int = 0, engine_time: int = 0, data: Schema = None,
#                  req=None,statistics:UltipaStatistics=None):
#         self.status = status
#         self.data = data
#         self.total_time = total_time
#         self.engine_time = engine_time
#         self.req = req
#         self.statistics = statistics


# class ResponseGeneric(Response, Generic[T]):
#     data: T


class ExportReply:
	def __init__(self, data: List[NodeAlias]):
		self.data = data


# class UQLSingleResponse(BaseModel):
#     def __init__(self):
#         self.responseWithoutData = Response
#         self.uqlReply = UqlReply


class UltipaConfig:
	hosts: List[str] = []
	defaultGraph: str = 'default'
	timeoutWithSeconds: int = 3600
	responseWithRequestInfo: bool = False
	# 读一致性,如果为False 负载取节点执行
	consistency: bool = False
	uqlLoggerConfig: LoggerConfig = None
	heartBeat: int = 10
	maxRecvSize: int
	Debug: bool = False
	timeZone = None
	timeZoneOffset = None

	def __init__(self, hosts=None, username=None, password=None, crtFilePath=None, defaultGraph: str = defaultGraph,
				 timeout: int = timeoutWithSeconds, responseWithRequestInfo: bool = responseWithRequestInfo,
				 consistency: bool = consistency, heartBeat: int = 10, maxRecvSize: int = -1,
				 uqlLoggerConfig: LoggerConfig = uqlLoggerConfig, debug: bool = False, timeZone=None,
				 timeZoneOffset=None, **kwargs):
		if hosts is None:
			hosts = []
		self.hosts = hosts
		self.username = username
		self.password = password
		self.crtFilePath = crtFilePath
		self.defaultGraph = defaultGraph
		self.timeoutWithSeconds = timeout
		self.responseWithRequestInfo = responseWithRequestInfo
		self.consistency = consistency
		self.uqlLoggerConfig = uqlLoggerConfig
		self.heartBeat = heartBeat
		self.maxRecvSize = maxRecvSize
		self.Debug = debug
		self.timeZone = timeZone
		self.timeZoneOffset = timeZoneOffset
		if kwargs.get("timeoutWithSeconds") is not None:
			self.timeoutWithSeconds = kwargs.get("timeoutWithSeconds")

	def setDefaultGraphName(self, graph: str):
		self.defaultGraph = graph


class PaserAttrListData:
	def __init__(self, type, nodes: List[Node]=None, edges: List[Edge]=None, paths: List[Path]=None, attrs: Attr=None):
		self.type = type
		self.nodes = nodes
		self.edges = edges
		self.paths = paths
		self.attrs = attrs


class OrderType(Enum):
	desc = 'desc'
	asc = 'asc'


class UltipaEquation(Enum):
	sum = 'sum'
	count = 'count'


InsertErrorCodeMsgMap = {10001: "uuid and id not match",
						 10002: "uuid/id and schema not match",
						 10003: "from_uuid and from_id not match",
						 10004: "to_uuid and to_id not match",
						 10005: "id length exceed max length(128 bytes)",
						 10006: "node value and schema value not match"
						 }

# class Schema:
#     def __init__(self,name:str):
#         self.name = "@"+name

if __name__ == "__main__":
	status = Status(Code.SUCCESS, "!23")
	print(status.code, status.message)
	pass
