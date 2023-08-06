from typing import List, Dict

from ultipa.printer.prettyPrint import PrettyPrint, PrettyTable
from ultipa.types.types import BaseModel, Node, Edge, DataItem, Status, \
	UltipaStatistics, Schema, ReturnReq, BaseUqlReply, ResultType, ResultAlias, ExplainPlan
from ultipa.utils.convert import Any


class Property(BaseModel):
	lte: bool
	index: bool
	propertyName: str
	propertyType: str
	description: str
	schema: str


class PropertyTable(BaseModel):
	name: str
	data: List[Property]

	def __init__(self, name, data):
		self.name = name
		self.data = data


class SchemaTable(BaseModel):
	name: str
	data: List[Schema]

	def __init__(self, name, data):
		self.name = name
		self.data = data


class Response(BaseModel):
	def __init__(self, status: Status = None, data: BaseUqlReply = None,
				 req: ReturnReq = None, statistics: UltipaStatistics = None, aliases: List[ResultAlias] = None):
		self.status = status
		self.data = data
		self.statistics = statistics
		self.req = req
		self.aliases = aliases

	def Print(self):
		pretty = PrettyPrint()
		pretty.prettyStatus(self.status)
		if self.status.code != 0:
			return
		if self.statistics:
			pretty.prettyStatistics(self.statistics)

		if isinstance(self.data, list):
			dict_list = [i.__dict__ for i in self.data]
			pretty.prettyDataList(dict_list)

		if isinstance(self.data, Any):
			dict_list = self.data.__dict__
			pretty.prettyData(dict_list)


class UltipaResponse(BaseModel):
	def __init__(self, status: Status = None, items: Dict = None,
				 req: ReturnReq = None, statistics: UltipaStatistics = None, aliases: List[ResultAlias] = None,
				 explainPlan: List[ExplainPlan] = None):
		self.status = status
		self.items = items
		self.aliases = aliases
		self.req = req
		self.statistics = statistics
		self.explainPlan = explainPlan

	def alias(self, alias: str) -> DataItem:
		if self.items == None:
			return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))
		if self.items.get(alias):
			return self.items.get(alias)
		return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))

	def get(self, index: int) -> DataItem:
		if len(self.aliases) - 1 >= index:
			data = self.items.get(self.aliases[index].alias)
			if data:
				return data
			if self.aliases[index].result_type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
				return DataItem(None, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))
			else:
				return data
		return DataItem(None, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))

	def getExplainPlan(self):
		return self.explainPlan

	def Print(self):
		pretty = PrettyPrint()
		pretty.prettyStatus(self.status)
		if self.status.code != 0:
			return
		pretty.prettyStatistics(self.statistics)
		explains = []
		for key in self.items:
			dataItem = self.items.get(key)
			if dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
				pretty.prettyNode(dataItem)

			elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
				pretty.prettyEdge(dataItem)

			elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
				pretty.prettyTable(dataItem)

			elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH):
				pretty.prettyPath(dataItem)

			elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR):
				pretty.prettyAttr(dataItem)

			# elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_ARRAY):
			# 	pretty.prettyArray(dataItem)

		if self.explainPlan:
			for explan in self.explainPlan:
				explains.append(explan)
			if explains:
				pretty.prettyTree(explains)


class SchemaResponse(BaseModel):
	def __init__(self, status: Status = None, total_time: int = 0, engine_time: int = 0, data: List[SchemaTable] = None,
				 req=None, statistics: UltipaStatistics = None):
		self.status = status
		self.data = data
		self.total_time = total_time
		self.engine_time = engine_time
		self.req = req
		self.statistics = statistics

	def Print(self):
		pretty = PrettyPrint()
		pretty.prettyStatus(self.status)
		if self.status.code != 0:
			return
		if self.statistics:
			pretty.prettyStatistics(self.statistics)
		for data in self.data:
			propertList = []
			if len(data.data) > 0:
				for index, header in enumerate(data.asTable().getHeaders()):
					propertList.append(header.get("property_name"))
			# if data.alias in ["_nodeSchema", "_edgeSchema"]:
			# 	if "properties" in propertList:
			# 		propertList.remove("properties")
			# 		propertList.append("properties")
			else:
				return

			y = PrettyTable(propertList, title=f"Alias: {data.name}")
			for row in data.asTable().getRows():
				y.add_row(row)
			print(y)

		# if isinstance(self.data,Any):
		#     dict_list = self.data.__dict__
		#     pretty.prettyData(dict_list)


class ResponseCommon(Response):
	data: None


# class GraphPrivilege(BaseModel):
#     name: str
#     values: List[str]
#
#     def __init__(self, name: str, values: List[str]):
#         self.name = name
#         self.values = values


class User(BaseModel):
	username: str
	create_time: str
	last_login_time: str
	graphPrivileges: dict
	systemPrivileges: List[str]
	policies: List[str]


class Index(BaseModel):
	name: str
	properties: str
	schema: str
	status: str


class IndexTable:
	name: str
	data: List[Index]


class Stat(BaseModel):
	cpuUsage: str
	memUsage: str
	company: str
	cpuCores: str
	expiredDate: str
	serverType: str
	version: str


class Graph(BaseModel):
	id: str
	name: str
	totalNodes: str
	totalEdges: str
	description: str
	status: str


class Privilege(BaseModel):
	graphPrivileges: List[str]
	systemPrivileges: List[str]


class Policy(BaseModel):
	name: str
	policies: List[str]
	graphPrivileges: dict
	systemPrivileges: List[str]


class Top(BaseModel):
	process_id: str
	process_uql: str
	duration: str


class Return_Type(BaseModel):
	is_realtime: bool
	is_visualization: bool
	is_wirte_back: bool


class Task_info(BaseModel):
	task_id: int
	algo_name: str
	start_time: int
	writing_start_time: int
	end_time: int
	time_cost: int
	TASK_STATUS: int
	status_code: str
	engine_cost: int
	return_type: Return_Type


class Task(BaseModel):
	param: dict
	task_info: Task_info
	result: dict


class SearchKhop(BaseModel):
	values: dict
	nodes: List[Node]


class Path(BaseModel):
	nodes: List[Node]
	edges: List[Edge]


class SearchPath(BaseModel):
	paths: List[Path]


class NodeSpread(SearchPath):
	pass


class AutoNet(SearchPath):
	pass


class AlgoResultOpt(BaseModel):
	can_realtime: bool
	can_visualization: bool
	can_write_back: bool


class Algo(BaseModel):
	param: dict
	name: str
	result_opt: AlgoResultOpt


class SearchAB(Response):
	data: SearchPath


class ResponseAutoNet(Response):
	data: AutoNet


class ResponseGraph(Response):
	data: Graph


class ResponseListGraph(Response):
	data: List[Graph]


class ResponseListIndex(UltipaResponse):
	data: List[IndexTable]


class ResponseListFulltextIndex(ResponseListIndex):
	pass


class ResponseSearchEdge(UltipaResponse):
	items: List[DataItem]


class ResponseSearchNode(UltipaResponse):
	items: List[DataItem]


class ResponseBulk:
	uuids: List[int]
	# ignore_indexes: List[int]
	errorItem: Dict


class ResponseInsert(Response):
	data: List[int]


class ResponseBulkInsert(Response):
	data: ResponseBulk


class ResponseBatchAutoInsert(Response):
	data: Dict[str, ResponseBulk]


class InsertResponse(Response):
	data: ResponseBulk


class ResponseNodeSpread(Response):
	data: NodeSpread


class ResponseListPolicy(Response):
	data: List[Policy]


class ResponsePolicy(Response):
	data: Policy


class ResponseListPrivilege(Response):
	data: List[Privilege]


class ResponseListProperty(Response):
	data: List[PropertyTable]


class ResponseGetProperty(Response):
	data: List[Property]


class ResponseSearchAB(Response):
	data: SearchAB


class ResponseSearchKhop(Response):
	data: SearchKhop


class ResponseListTop(Response):
	data: List[Top]


class ResponseListTask(Response):
	data: List[Task]


class ResponseUser(Response):
	data: User


class ResponseListUser(Response):
	data: List[User]


class ResponseListAlgo(Response):
	data: List[Algo]


class Cluster:
	host: str
	status: bool
	cpuUsage: str
	memUsage: str
	isLeader: bool
	isFollowerReadable: bool
	isAlgoExecutable: bool
	isUnset: bool


class ClusterInfo(Response):
	data: List[Cluster]


class ResponseStat(Response):
	data: Stat


class ResponseExport(Response):
	data: List[Node]


