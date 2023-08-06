# -*-coding:utf-8-*-
import copy
import csv
import json
import random
import time
import types
from datetime import datetime
from typing import Iterable, List
import logging
import grpc
import pytz
import schedule
from tzlocal import get_localzone
from ultipa.proto import ultipa_pb2
from ultipa.proto import ultipa_pb2_grpc
from ultipa.types import ULTIPA, ULTIPA_REQUEST, ULTIPA_RESPONSE
from ultipa.types.types import UltipaConfig, LoggerConfig
from ultipa.types.types_response import PropertyTable
from ultipa.utils import CommandList, errors
from ultipa.utils.common import GETLEADER_TIMEOUT
from ultipa.utils.convert import convertToListAnyObject, convertTableToDict
from ultipa.utils.errors import ParameterException
from ultipa.utils.format import FormatType
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.password2md5 import passwrod2md5
from ultipa.utils.raftRetry import RetryHelp
from ultipa.utils.ultipaSchedule import run_continuously
from ultipa.utils.ultipa_datetime import getTimeZoneOffset
from ultipa.utils.uql_marker import UQL
from ultipa.utils.uql_marker import UQLMAKER

RAFT_GLOBAL = "global"


class GetProperty():
	node: str = 'show().node_property()'
	edge: str = 'show().edge_property()'


class GetPropertyBySchema():
	node: str = 'show().node_schema()'
	edge: str = 'show().edge_schema()'


# @staticmethod
# def node(schemaName:str):
#     return f"show().node_schema()"
#
# @staticmethod
# def edge(schemaName: str):
#     return f"show().edge_schema()"


class ClientType:
	Default = 0  # 默认
	Algo = 1  # 算法
	Update = 2  # 更新
	Leader = 3  # 主节点


class GrpcClientInfo:
	Rpcsclient: ultipa_pb2_grpc.UltipaRpcsStub
	Controlsclient: ultipa_pb2_grpc.UltipaControlsStub
	host: str
	username: str
	password: str

	def __init__(self, host: str, username: str, password: str, crt: str, maxRecvSize: int = -1):
		self.host = host
		self._metadata = [('user', username), ('password', passwrod2md5(password))]
		if crt:
			credentials = grpc.ssl_channel_credentials(root_certificates=crt)
			channel = grpc.secure_channel(self.host, credentials, options=(
				('grpc.ssl_target_name_override', 'ultipa'), ('grpc.default_authority', 'ultipa'),
				('grpc.max_send_message_length', -1), ('grpc.max_receive_message_length', maxRecvSize),
				("grpc.keepalive_timeout_ms", 1500)
			))
			self.Rpcsclient = ultipa_pb2_grpc.UltipaRpcsStub(channel=channel, )
			self.Controlsclient = ultipa_pb2_grpc.UltipaControlsStub(channel=channel, )
		else:
			channel = grpc.insecure_channel(self.host, options=(
				('grpc.max_send_message_length', -1), ('grpc.max_receive_message_length', maxRecvSize),
				("grpc.keepalive_timeout_ms", 1500)))
			self.Rpcsclient = ultipa_pb2_grpc.UltipaRpcsStub(channel=channel, )
			self.Controlsclient = ultipa_pb2_grpc.UltipaControlsStub(channel=channel, )

	def getMetadata(self, graphSetName, timeZone, timeZoneOffset):
		metadata = copy.deepcopy(self._metadata)
		metadata.append(('graph_name', graphSetName))
		if timeZone is None and timeZoneOffset is None:
			timeZone = get_localzone().__dict__.get("_key")
			tz = pytz.timezone(timeZone)
			timeZoneOffset = tz.utcoffset(datetime.now()).total_seconds()
			metadata.append(('tz_offset', str(timeZoneOffset)))
		if timeZone is not None and timeZoneOffset is None:
			metadata.append(('tz', timeZone))
		if timeZone is None and timeZoneOffset is not None:
			metadata.append(('tz_offset', str(timeZoneOffset)))
		return metadata


class UQLHelper:
	_globalCommand = [
		CommandList.createUser,
		CommandList.showUser,
		CommandList.alterUser,
		CommandList.getUser,
		CommandList.dropUser,
		CommandList.grant,
		CommandList.revoke,
		CommandList.showPolicy,
		CommandList.getPolicy,
		CommandList.createPolicy,
		CommandList.alterPolicy,
		CommandList.dropPolicy,
		CommandList.showPrivilege,
		CommandList.stat,
		CommandList.createGraph,
		CommandList.showGraph,
		CommandList.dropGraph,
		CommandList.alterGraph,
		CommandList.top,
		CommandList.kill,
		# CommandList.mount,
		# CommandList.unmount
	]
	_write = [
		"alter",
		"create",
		"drop",
		"grant",
		"revoke",
		"LTE",
		"UFE",
		"truncate",
		"compact",
		"insert",
		"upsert",
		"update",
		"delete",
		"clear",
		"stop",
		"pause",
		"resume",
		"top",
		"kill",
		"mount",
		"unmount",
	]
	_extra = [
		CommandList.top,
		CommandList.kill,
		CommandList.showTask,
		CommandList.stopTask,
		CommandList.clearTask,
		CommandList.stat,
		CommandList.showGraph,
		CommandList.showAlgo,
		CommandList.createPolicy,
		CommandList.dropPolicy,
		CommandList.showPolicy,
		CommandList.getPolicy,
		CommandList.grant,
		CommandList.revoke,
		CommandList.showPrivilege,
		CommandList.showUser,
		CommandList.getSelfInfo,
		CommandList.createUser,
		CommandList.alterUser,
		CommandList.dropUser,
		CommandList.showIndex,
		# CommandList.clearTask,
	]

	def __init__(self, uql: str):
		self.uql = uql
		self.parseRet = UQL.parse(uql)

	def uqlIsGlobal(self):
		# p = UQL.parse_globle(uql)
		# if p != None:
		#     for command in p.commands:
		#         if command in UQLHelper._globalCommand:
		#             return True

		if self.parseRet != None:
			c1 = self.parseRet.getFirstCommands()
			c2 = f"{c1}().{self.parseRet.getSecondCommands()}"
			return c1 in UQLHelper._globalCommand or c2 in UQLHelper._globalCommand
		return False

	@staticmethod
	def uqlIsWrite(uql: str):
		p = UQL.parse(uql)
		if p != None:
			for command in p.commands:
				if list(filter(lambda x: x == command, UQLHelper._write)):
					return True
		return False

	@staticmethod
	def uqlIsAlgo(uql: str):
		p = UQL.parse(uql)
		if p != None:
			for command in p.commands:
				if command == 'algo':
					return True
		# return p.command == 'algo'
		return False

	@staticmethod
	def uqlIsExecTask(uql: str):
		return "exec task" in uql.lower()

	@staticmethod
	def uqlIsExtra(uql: str):
		p = UQL.parse(uql)
		if p != None:
			c1 = p.getFirstCommands()
			c2 = f"{c1}().{p.getSecondCommands()}"
			return c1 in UQLHelper._extra or c2 in UQLHelper._extra
		return False


class ClientInfo:
	def __init__(self, Rpcsclient: ultipa_pb2_grpc.UltipaRpcsStub, Controlsclient: ultipa_pb2_grpc.UltipaControlsStub,
				 metadata: any, graphSetName: str, host: str):
		self.Rpcsclient = Rpcsclient
		self.Controlsclient = Controlsclient
		self.host = host
		self.metadata = metadata
		self.graphSetName = graphSetName


class HostManagerControl:
	initHost: str = None
	username: str = None
	password: str = None
	crt: str = None
	allHostManager: dict = {}
	consistency: bool = False

	def __init__(self, initHost: str, username: str, password: str, maxRecvSize: int = -1, crt: str = None,
				 consistency: bool = False):
		self.initHost = initHost
		self.username = username
		self.password = password
		self.maxRecvSize = maxRecvSize
		self.consistency = consistency
		self.crt = crt
		self.allHostManager = {}

	def chooseClientInfo(self, type: int, uql: str, graphSetName: str, useHost: str = None, useMaster: bool = False):
		hostManager = self.getHostManger(graphSetName)
		return hostManager.chooseClientInfo(type, uql, consistency=self.consistency,
											useHost=useHost, useMaster=useMaster)

	def upsetHostManger(self, graphSetName: str, initHost: str):
		hostManager = HostManager(graphSetName=graphSetName, host=initHost, username=self.username,
								  password=self.password, crt=self.crt, maxRecvSize=self.maxRecvSize)
		self.allHostManager[graphSetName] = hostManager
		return hostManager

	def getHostManger(self, graphSetName: str):
		hostManager = self.allHostManager.get(graphSetName)
		if not hostManager:
			hostManager = self.upsetHostManger(graphSetName=graphSetName, initHost=self.initHost)
		return hostManager

	def getAllHosts(self):
		hostManager = self.getHostManger(RAFT_GLOBAL)
		return hostManager.getAllHosts()

	def getAllClientInfos(self, graph):
		return self.getHostManger(graph).getAllClientInfos(ignoreAlgo=True)

	def getAllHostStatusInfo(self, graph):
		all: List[ULTIPA.RaftPeerInfo] = []
		all.extend(self.getHostManger(graph).followersPeerInfos)
		all.append(self.getHostManger(graph).leaderInfos)
		return all


class HostManager:
	username: str
	password: str
	crt: str
	graphSetName: str
	leaderHost: str
	followersPeerInfos: List[ULTIPA.RaftPeerInfo] = None
	leaderInfos: ULTIPA.RaftPeerInfo = None
	leaderClientInfo: GrpcClientInfo = None
	algoClientInfos: List[GrpcClientInfo] = []
	defaultClientInfo: GrpcClientInfo = None
	otherFollowerClientInfos: List[GrpcClientInfo] = []
	otherUnsetFollowerClientInfos: List[GrpcClientInfo] = []
	nullClientInfos: GrpcClientInfo = None
	raftReady: bool = False

	def __init__(self, graphSetName: str, host: str, username: str, password: str, crt: str, maxRecvSize: int):
		self.graphSetName = graphSetName
		self.username = username
		self.password = password
		self.maxRecvSize = maxRecvSize
		self.leaderHost = host
		self.crt = crt
		self.defaultClientInfo = self.__createClientInfo(host)
		self.nullClientInfos = self.__createClientInfo('0.0.0.0')

	def __createClientInfo(self, host: str):

		if self.leaderClientInfo and self.leaderClientInfo.host == host:
			return self.leaderClientInfo

		if self.defaultClientInfo and self.defaultClientInfo.host == host:
			return self.defaultClientInfo

		clientInfo = GrpcClientInfo(host=host, username=self.username, password=self.password, crt=self.crt,
									maxRecvSize=self.maxRecvSize)
		return clientInfo

	def chooseClientInfo(self, clientType: int, uql: str, consistency: bool, useHost: str, useMaster: bool):
		'''
		三个原则：写发给leader、算法发给follower，读三个节点负载均衡
		选择连接对象
		:param clientType: 连接的类型
		:return:
		'''
		if useMaster:
			return self.leaderClientInfo or self.defaultClientInfo

		clientType = clientType or ClientType.Default
		if uql:
			# 如果没有type，并且有uql，根据uql自动判断
			if UQLHelper.uqlIsExecTask(uql):
				clientType = ClientType.Algo
			elif UQLHelper.uqlIsWrite(uql):
				clientType = ClientType.Update
		# elif UQLHelper.uqlIsGlobal(uql):
		#     clientType = ClientType.Leader
		if clientType == ClientType.Algo:
			if not self.algoClientInfos:
				return self.nullClientInfos
			return random.choice(self.algoClientInfos)
		if clientType == ClientType.Update or clientType == ClientType.Leader or consistency:
			return self.leaderClientInfo or self.defaultClientInfo

		if useHost:
			for clientInfo in self.getAllClientInfos():
				if useHost == clientInfo.host:
					return clientInfo
			# 如果没有找到usehost 直接返回没有连接的
			return self.__createClientInfo(useHost)

		# 负载均衡，随机取除算法外的clientInfo中的其中一个'
		return random.choice(list(self.getAllClientInfos(ignoreAlgo=True, needUnset=False)))

	def getAllHosts(self):
		hosts = [self.leaderHost]
		if self.followersPeerInfos:
			for PeerHost in self.followersPeerInfos:
				hosts.append(PeerHost.host)
		return hosts

	def getAllClientInfos(self, ignoreAlgo: bool = False, needUnset: bool = True):
		all = [self.defaultClientInfo]
		if self.leaderClientInfo and self.leaderClientInfo.host != self.defaultClientInfo.host:
			all.append(self.leaderClientInfo)
		if self.algoClientInfos and not ignoreAlgo:
			all.extend(self.algoClientInfos)
		if self.otherFollowerClientInfos:
			all.extend(self.otherFollowerClientInfos)
		if self.otherUnsetFollowerClientInfos and needUnset:
			all.extend(self.otherUnsetFollowerClientInfos)
		return all

	def setClients(self, leaderHost: str, followersPeerInfos: List[ULTIPA.RaftPeerInfo],
				   leaderInfos: ULTIPA.RaftPeerInfo):

		self.leaderHost = leaderHost
		self.leaderClientInfo = self.__createClientInfo(leaderHost)
		self.followersPeerInfos = followersPeerInfos
		self.leaderInfos = leaderInfos
		self.otherFollowerClientInfos = []
		self.otherUnsetFollowerClientInfos = []
		self.algoClientInfos = []

		if followersPeerInfos and len(followersPeerInfos) > 0:
			for peerInfo in followersPeerInfos:

				if peerInfo.isAlgoExecutable:
					self.algoClientInfos.append(self.__createClientInfo(peerInfo.host))

				if peerInfo.isFollowerReadable:
					self.otherFollowerClientInfos.append(self.__createClientInfo(peerInfo.host))

				if peerInfo.isUnset:
					self.otherUnsetFollowerClientInfos.append(self.__createClientInfo(peerInfo.host))
		else:
			# 如果没有，则使用leader做为算法节点
			self.algoClientInfos = [self.leaderClientInfo]


class ConnectionBase:
	hostManagerControl: HostManagerControl
	username: str
	password: str
	crtPath: str
	defaultConfig: UltipaConfig
	runSchedule: object = None

	def __init__(self, host: str, defaultConfig: UltipaConfig, crtFilePath: str = None):
		# if pwdIsmd5:
		#     defaultConfig.password = passwrod2md5(defaultConfig.password) if defaultConfig.password else defaultConfig.password
		self.host = host
		self.username = defaultConfig.username
		self.password = defaultConfig.password
		self.crtPath = crtFilePath
		self.defaultConfig = defaultConfig
		self.crt = None
		if crtFilePath:
			try:
				with open(f'{crtFilePath}', 'rb') as f:
					self.crt = f.read()
			except Exception as e:
				raise ParameterException(err=e)
		self.hostManagerControl = HostManagerControl(self.host, self.username, self.password,
													 self.defaultConfig.maxRecvSize, self.crt,
													 consistency=defaultConfig.consistency)

		self.defaultConfig.defaultGraph = defaultConfig.defaultGraph or "default"
		self.defaultConfig.timeoutWithSeconds = defaultConfig.timeoutWithSeconds or 15
		self.defaultConfig.responseWithRequestInfo = defaultConfig.responseWithRequestInfo or False
		self.defaultConfig.consistency = defaultConfig.consistency
		self.graphSetName = self.defaultConfig.defaultGraph
		self.count = 0

		# 如果DEBUG 实例化 logger 那就用ultipa 的
		if not self.defaultConfig.uqlLoggerConfig and self.defaultConfig.Debug:
			self.defaultConfig.uqlLoggerConfig = LoggerConfig(name="ultipa", fileName="",
															  isStream=self.defaultConfig.Debug, isWriteToFile=False,
															  level=logging.INFO)

	# def uql(self, uql: str,
	# 		requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
	# 	request = ultipa_pb2.UqlRequest()
	# 	request.uql = uql
	# 	request.timeout = self.getTimeout(requestConfig.timeoutWithSeconds)
	# 	request.thread_num = requestConfig.threadNum
	# 	errorRes = ULTIPA_RESPONSE.UltipaResponse()
	# 	uqlLoggerConfig = self.defaultConfig.uqlLoggerConfig
	# 	if requestConfig.graphName == '' and self.defaultConfig.defaultGraph != '':
	# 		requestConfig.graphName = self.defaultConfig.defaultGraph
	#
	# 	if self.defaultConfig.consistency != self.hostManagerControl.consistency:
	# 		self.hostManagerControl.consistency = self.defaultConfig.consistency
	#
	# 	if self.defaultConfig.maxRecvSize != self.hostManagerControl.maxRecvSize:
	# 		self.hostManagerControl.maxRecvSize = self.defaultConfig.maxRecvSize
	# 	try:
	# 		if self.hostManagerControl.getHostManger(requestConfig.graphName):
	# 			graphHost = self.hostManagerControl.getHostManger(requestConfig.graphName).leaderHost
	# 			if not self.test(ULTIPA_REQUEST.RequestConfig(host=graphHost)):
	# 				self.hostManagerControl.getHostManger(requestConfig.graphName).raftReady = False
	# 				if graphHost in self.defaultConfig.hosts:
	# 					self.defaultConfig.hosts.remove(graphHost)
	# 		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, uql=uql,
	# 										useHost=requestConfig.useHost,
	# 										useMaster=requestConfig.useMaster)
	# 		if uqlLoggerConfig:
	# 			uqlLoggerConfig.getlogger().info(
	# 				f'Begin UQL: {uql} graphSetName: {clientInfo.graphSetName} Host: {self.host}')
	# 		uqlIsExtra = UQLHelper.uqlIsExtra(uql)
	# 		if uqlIsExtra:
	# 			res = clientInfo.Controlsclient.UqlEx(request, metadata=clientInfo.metadata)
	# 		else:
	# 			res = clientInfo.Rpcsclient.Uql(request, metadata=clientInfo.metadata)
	#
	# 		if not requestConfig.stream:
	# 			res = FormatType.uqlMergeResponse(res)
	# 		else:
	# 			res = FormatType.uqlResponse(_res=res)
	# 			if not isinstance(res, Iterable):
	# 				reTry = RetryHelp.check(self, requestConfig, res)
	# 				if reTry.canRetry:
	# 					requestConfig.retry = reTry.nextRetry
	# 					return self.uql(uql, requestConfig)
	# 			return res
	#
	# 		reTry = RetryHelp.check(self, requestConfig, res)
	# 		if reTry.canRetry:
	# 			requestConfig.retry = reTry.nextRetry
	# 			return self.uql(uql, requestConfig)
	#
	# 		if self.defaultConfig.responseWithRequestInfo and not requestConfig.stream:
	# 			res.req = ULTIPA.ReturnReq(clientInfo.graphSetName, uql, clientInfo.host, requestConfig.retry,
	# 									   uqlIsExtra)
	# 		return res
	#
	# 	except Exception as e:
	#
	# 		try:
	# 			message = str(e._state.code) + ' : ' + str(e._state.details)
	# 		except:
	# 			message = str(e)
	#
	# 		# if errorRes.status == None:
	# 		errorRes.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
	# 		errorRes.req = ULTIPA.ReturnReq(requestConfig.graphName, uql,
	# 										requestConfig.useHost if requestConfig.useHost else self.host, requestConfig.retry,
	# 										False)
	# 		return errorRes

	def uql(self, uql: str,
			requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		request = ultipa_pb2.UqlRequest()
		request.uql = uql
		request.timeout = self.getTimeout(requestConfig.timeoutWithSeconds)
		if requestConfig.threadNum is not None:
			request.thread_num = requestConfig.threadNum
		ultipaRes = ULTIPA_RESPONSE.UltipaResponse()
		uqlLoggerConfig = self.defaultConfig.uqlLoggerConfig
		if requestConfig.graphName == '' and self.defaultConfig.defaultGraph != '':
			requestConfig.graphName = self.defaultConfig.defaultGraph

		if self.defaultConfig.consistency != self.hostManagerControl.consistency:
			self.hostManagerControl.consistency = self.defaultConfig.consistency

		if self.defaultConfig.maxRecvSize != self.hostManagerControl.maxRecvSize:
			self.hostManagerControl.maxRecvSize = self.defaultConfig.maxRecvSize
		onRetry = copy.deepcopy(requestConfig.retry)
		while onRetry.current < onRetry.max:
			try:
				import pytz
				timeZone = requestConfig.timeZone if requestConfig.timeZone else self.defaultConfig.timeZone
				if timeZone is not None:
					try:
						pytz.timezone(timeZone)
					except pytz.exceptions.UnknownTimeZoneError as e:
						raise errors.ParameterException("UnknownTimeZoneError:" + str(e))
				timeZoneOffset = requestConfig.timeZoneOffset if requestConfig.timeZoneOffset else self.defaultConfig.timeZoneOffset
				if timeZoneOffset is not None and type(timeZoneOffset) is not int:
					raise errors.ParameterException("timeZoneOffset:" + str(timeZoneOffset))

				clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, uql=uql,
												useHost=requestConfig.useHost,
												useMaster=requestConfig.useMaster, timezone=timeZone,
												timeZoneOffset=timeZoneOffset)
				if uqlLoggerConfig:
					uqlLoggerConfig.getlogger().info(
						f'Begin UQL: {uql} graphSetName: {clientInfo.graphSetName} Host: {clientInfo.host}')
				uqlIsExtra = UQLHelper.uqlIsExtra(uql)
				if uqlIsExtra:
					res = clientInfo.Controlsclient.UqlEx(request, metadata=clientInfo.metadata)
				else:
					res = clientInfo.Rpcsclient.Uql(request, metadata=clientInfo.metadata)

				if not requestConfig.stream:
					ultipaRes = FormatType.uqlMergeResponse(res, timeZone, timeZoneOffset)
				else:
					ultipaRes = FormatType.uqlResponse(res, timeZone, timeZoneOffset)

				if self.defaultConfig.responseWithRequestInfo and not requestConfig.stream:
					ultipaRes.req = ULTIPA.ReturnReq(clientInfo.graphSetName, uql, clientInfo.host, onRetry,
													 uqlIsExtra)
				if not isinstance(ultipaRes, types.GeneratorType) and RetryHelp.checkRes(ultipaRes):
					onRetry.current += 1
					continue
				else:
					return ultipaRes

			except Exception as e:
				onRetry.current += 1
				if uqlLoggerConfig:
					uqlLoggerConfig.getlogger().info(
						f'Begin Retry [{onRetry.current}]- clientInfo host: {clientInfo.host} graphSetName: {clientInfo.graphSetName}')
				self.hostManagerControl.getHostManger(requestConfig.graphName).raftReady = False
				try:
					message = str(e._state.code) + ' : ' + str(e._state.details)
				except:
					message = str(e)
				# if errorRes.status == None:
				ultipaRes.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
				ultipaRes.req = ULTIPA.ReturnReq(requestConfig.graphName, uql,
												 requestConfig.useHost if requestConfig.useHost else self.host,
												 onRetry, False)

		return ultipaRes

	def uqlSingle(self, uqlMaker: UQLMAKER) -> ULTIPA_RESPONSE.UltipaResponse:
		res = self.uql(uqlMaker.toString(), uqlMaker.commonParams)
		return res

	def getGraphSetName(self, currentGraphName: str, uql: str = "", isGlobal: bool = False):
		if isGlobal:
			return RAFT_GLOBAL
		if uql:
			parse = UQLHelper(uql)
			if parse.uqlIsGlobal():
				return RAFT_GLOBAL
			# // truncate，mount，unmount，update, 发给当前图集
			c1 = parse.parseRet.getFirstCommands()
			c2 = f"{c1}().{parse.parseRet.getSecondCommands()}"
			if c2 in [CommandList.mount, CommandList.unmount, CommandList.truncate]:
				graphName = parse.parseRet.getCommandsParam(1)
				if graphName:
					return graphName
		return currentGraphName or self.defaultConfig.defaultGraph

	def getTimeout(self, timeout: int):
		return timeout or self.defaultConfig.timeoutWithSeconds

	@staticmethod
	def UqlListSimple(conn: 'ConnectionBase', uqlMaker: UQLMAKER, responseKeyFormat: ResponseKeyFormat = None,
					  isSingleOne: bool = True) -> ULTIPA_RESPONSE.Response:
		res = conn.uqlSingle(uqlMaker)

		if res.status.code != ULTIPA.Code.SUCCESS:
			simplrRes = ULTIPA_RESPONSE.Response(res.status, res.items)
			return simplrRes

		if not isSingleOne:
			retList = []
			for alias in res.aliases:
				item = res.items.get(alias.alias)
				table = item.data
				table_rows = table.rows
				table_rows_dict = convertTableToDict(table_rows, table.headers)
				if responseKeyFormat:
					table_rows_dict = responseKeyFormat.changeKeyValue(table_rows_dict)
				data = convertToListAnyObject(table_rows_dict)
				retList.append(PropertyTable(name=table.name, data=data))
			simplrRes = ULTIPA_RESPONSE.Response(res.status, retList)
			simplrRes.req = res.req
			return simplrRes

		alisFirst = res.aliases[0].alias if len(res.aliases) > 0 else None
		firstItem = res.items.get(alisFirst)
		if firstItem:
			table_rows = firstItem.data.rows
			table_rows_dict = convertTableToDict(table_rows, firstItem.data.headers)
			if responseKeyFormat:
				table_rows_dict = responseKeyFormat.changeKeyValue(table_rows_dict)
			data = convertToListAnyObject(table_rows_dict)
			simplrRes = ULTIPA_RESPONSE.Response(res.status, data)
			simplrRes.req = res.req
			simplrRes.statistics = res.statistics
			return simplrRes
		else:
			return res

	@staticmethod
	def UqlUpdateSimple(conn: 'ConnectionBase', uqlMaker: UQLMAKER):
		res = conn.uqlSingle(uqlMaker)

		if res.status.code != ULTIPA.Code.SUCCESS:
			return ULTIPA_RESPONSE.Response(res.status, statistics=res.statistics)

		if res.req:
			ret = ULTIPA_RESPONSE.Response(res.status, statistics=res.statistics)
			ret.req = res.req
			return ret
		return ULTIPA_RESPONSE.Response(res.status, statistics=res.statistics)

	def getClientInfo(self, clientType: int = ClientType.Default, graphSetName: str = '', uql: str = '',
					  isGlobal: bool = False, ignoreRaft: bool = False, useHost: str = None, useMaster: bool = False,
					  timezone=None, timeZoneOffset=None):
		goGraphName = self.getGraphSetName(currentGraphName=graphSetName, uql=uql, isGlobal=isGlobal)
		if not ignoreRaft and not self.hostManagerControl.getHostManger(goGraphName).raftReady:
			refreshRet = self.refreshRaftLeader(self.hostManagerControl.initHost,
												ULTIPA_REQUEST.RequestConfig(graphName=goGraphName))
			self.hostManagerControl.getHostManger(goGraphName).raftReady = refreshRet

		clientInfo = self.hostManagerControl.chooseClientInfo(type=clientType, uql=uql, graphSetName=goGraphName,
															  useHost=useHost, useMaster=useMaster)
		metadata = clientInfo.getMetadata(goGraphName, timezone, timeZoneOffset)
		return ClientInfo(Rpcsclient=clientInfo.Rpcsclient, Controlsclient=clientInfo.Controlsclient, metadata=metadata,
						  graphSetName=goGraphName, host=clientInfo.host)

	def test(self,
			 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		testResponse = ULTIPA_RESPONSE.Response()
		returnReq = ULTIPA.ReturnReq(requestConfig.graphName, "test", None, None, False)
		try:
			clientInfo = self.getClientInfo(useHost=requestConfig.useHost, useMaster=requestConfig.useMaster)
			name = 'Test'
			res = clientInfo.Controlsclient.SayHello(ultipa_pb2.HelloUltipaRequest(name=name),
													 metadata=clientInfo.metadata)
			returnReq.host = clientInfo.host
			if (res.message == name + " Welcome To Ultipa!"):
				if self.defaultConfig.uqlLoggerConfig:
					self.defaultConfig.uqlLoggerConfig.getlogger().info(res.message)

				testResponse.status = ULTIPA.Status(code=res.status.error_code, message=res.status.msg)
			else:
				testResponse.status = ULTIPA.Status(code=res.status.error_code, message=res.status.msg)
		except Exception as e:
			# print(e)
			testResponse = ULTIPA_RESPONSE.Response()
			try:
				message = str(e._state.details)
			except:
				message = str(e)
			testResponse.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
		if self.defaultConfig.responseWithRequestInfo:
			testResponse.req = returnReq
		return testResponse

	def exportData(self, request: ULTIPA_REQUEST.Export,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		try:
			req = ultipa_pb2.ExportRequest(db_type=request.type, limit=request.limit,
										   select_properties=request.properties, schema=request.schema)

			clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster)
			res = clientInfo.Controlsclient.Export(req, metadata=clientInfo.metadata)
			res = FormatType.exportResponse(_res=res, timeZone=requestConfig.timeZone,
											timeZoneOffset=requestConfig.timeZoneOffset)
			return res
		except Exception as e:
			errorRes = ULTIPA_RESPONSE.Response()
			try:
				message = str(e._state.code) + ' : ' + str(e._state.details)
			except:
				message = 'UNKNOW ERROR'

			errorRes.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
			errorRes.req = ULTIPA.ReturnReq(self.graphSetName, "exportData",
											requestConfig.useHost if requestConfig.useHost else self.host,
											requestConfig.retry,
											False)
			return errorRes

	def getRaftLeader(self, requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		resRaftLeader = self.__autoGetRaftLeader(host=self.host, requestConfig=requestConfig)
		RaftStatus = FormatType.getRaftStatus(resRaftLeader)
		return ULTIPA_RESPONSE.Response(RaftStatus)

	def __getRaftLeader(self, requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		if requestConfig == None:
			graphSetName = None
		else:
			if not requestConfig.graphName:
				graphSetName = 'default'
			else:
				graphSetName = requestConfig.graphName

		clientInfo = self.getClientInfo(clientType=ClientType.Leader, graphSetName=graphSetName, ignoreRaft=True,
										useMaster=requestConfig.useMaster)
		res = clientInfo.Controlsclient.GetLeader(ultipa_pb2.GetLeaderRequest(), metadata=clientInfo.metadata,
												  timeout=GETLEADER_TIMEOUT)

		return FormatType.Response(_res=res, host=self.host)

	def __autoGetRaftLeader(self, host: str, requestConfig: ULTIPA_REQUEST.RequestConfig, retry=0):
		'''内部用，所以返回值自定义'''
		conn = ConnectionBase(host=host, crtFilePath=self.crtPath, defaultConfig=self.defaultConfig)
		try:
			res = conn.__getRaftLeader(requestConfig)
		except Exception as e:
			self.hostManagerControl.initHost = ""
			if host in self.defaultConfig.hosts:
				self.defaultConfig.hosts.remove(host)
			return {
				"code": ULTIPA.Code.FAILED,
				"message": str(e._state.code) + ' : ' + str(e._state.details)
			}
		status = res.status
		if status.code == ULTIPA.Code.SUCCESS:
			# status.clusterInfo.raftPeers.remove(host)  # 不要主节点
			self.hostManagerControl.initHost = host
			for i in status.clusterInfo.raftPeers:
				if i.host == host:
					status.clusterInfo.raftPeers.remove(i)
			return {
				"code": status.code,
				"message": status.message,
				'leaderHost': host,
				"followersPeerInfos": list(filter(lambda x: x != host, status.clusterInfo.raftPeers)),
				"leaderInfos": status.clusterInfo.leader,
			}
		elif status.code == ULTIPA.Code.NOT_RAFT_MODE:
			return {
				"code": status.code,
				"message": status.message,
				"leaderHost": host,
				"followersPeerInfos": [],
				"leaderInfos": status.clusterInfo.leader
			}
		elif status.code in [ULTIPA.Code.RAFT_REDIRECT, ULTIPA.Code.RAFT_LEADER_NOT_YET_ELECTED,
							 ULTIPA.Code.RAFT_NO_AVAILABLE_FOLLOWERS, ULTIPA.Code.RAFT_NO_AVAILABLE_ALGO_SERVERS]:
			if retry > 2:
				return {
					"code": status.code,
					"message": status.message,
					"redirectHost": res.status.clusterInfo.redirect
				}
			if status.code != ULTIPA.Code.RAFT_REDIRECT:
				time.sleep(0.3)
			if status.code == ULTIPA.Code.RAFT_REDIRECT:
				host = res.status.clusterInfo.redirect
			return self.__autoGetRaftLeader(host=host, requestConfig=requestConfig, retry=retry + 1)

		return {
			"code": status.code,
			"message": status.message
		}

	def refreshRaftLeader(self, redirectHost: str, requestConfig: ULTIPA_REQUEST.RequestConfig):
		# hosts = [redirectHost] if redirectHost else self.hostManagerControl.getAllHosts()
		hosts = [redirectHost] if redirectHost else []
		goGraphName = self.getGraphSetName(requestConfig.graphName)

		for h in self.defaultConfig.hosts:
			if h not in hosts:
				hosts.append(h)
		for host in hosts:
			resRaftLeader = self.__autoGetRaftLeader(host=host, requestConfig=requestConfig)
			code = resRaftLeader["code"]
			if code == ULTIPA.Code.SUCCESS:
				leaderHost = resRaftLeader["leaderHost"]
				followersPeerInfos = resRaftLeader["followersPeerInfos"]
				leaderInfos = resRaftLeader["leaderInfos"]
				hostManager = self.hostManagerControl.upsetHostManger(goGraphName, leaderHost)
				hostManager.setClients(leaderHost=leaderHost, followersPeerInfos=followersPeerInfos,
									   leaderInfos=leaderInfos)
				return True
		# elif code == ULTIPA.Code.RAFT_REDIRECT:
		# 	return False
		return False

	def stats(self,
			  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseStat:
		uqlMaker = UQLMAKER(command=CommandList.stat, commonParams=requestConfig)
		ret = ConnectionBase.UqlListSimple(self, uqlMaker=uqlMaker, isSingleOne=True)
		if ret.status.code == ULTIPA.Code.SUCCESS:
			ret.data = ret.data[0]
		return ret

	def _insertNodesBulk(self, insertReq: ULTIPA_REQUEST.InsertNodeBulk,
						 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseBulkInsert:
		req = copy.deepcopy(insertReq)
		try:
			if requestConfig.graphName == '' and self.defaultConfig.defaultGraph != '':
				requestConfig.graphName = self.defaultConfig.defaultGraph
			clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=requestConfig.graphName,
											useMaster=requestConfig.useMaster)
			propertyRet = self.uql(GetPropertyBySchema.node,
								   ULTIPA_REQUEST.RequestConfig(graphName=requestConfig.graphName))
			schemaDict = None
			if propertyRet.status.code == ULTIPA.Code.SUCCESS:
				for aliase in propertyRet.aliases:
					if aliase.alias == '_nodeSchema':
						schemaDict = convertTableToDict(propertyRet.alias(aliase.alias).data.rows,
														propertyRet.alias(aliase.alias).data.headers)
				if not schemaDict:
					raise ParameterException(err='Please create Node Schema')

			else:
				raise ParameterException(err=propertyRet.status.message)

			# nodeTable = FormatType.toNodeTable(nodeSchamHeaders, req.rows)
			nodeTable = FormatType.toNodeTableSingle(schemaDict, req.schema, req.rows,
													 getTimeZoneOffset(requestConfig=insertReq,
																	   defaultConfig=self.defaultConfig))
			_nodeTable = ultipa_pb2.NodeTable(schemas=nodeTable.schemas, node_rows=nodeTable.nodeRows)
			request = ultipa_pb2.InsertNodesRequest()
			request.silent = req.silent
			request.insert_type = req.insertType
			request.graph_name = requestConfig.graphName
			request.node_table.MergeFrom(_nodeTable)
			res = clientInfo.Rpcsclient.InsertNodes(request, metadata=clientInfo.metadata)
		except Exception as e:
			errorRes = ULTIPA_RESPONSE.Response()
			try:
				message = str(e._state.code) + ' : ' + str(e._state.details)
			except:
				message = str(e)

			errorRes.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
			errorRes.req = ULTIPA.ReturnReq(requestConfig.graphName, "insertNodesBulk",
											requestConfig.useHost if requestConfig.useHost else self.host,
											requestConfig.retry, False)
			return errorRes

		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, requestConfig, uqlres)
		if reTry.canRetry:
			requestConfig.retry = reTry.nextRetry
			return self.insertNodesBulk(req, requestConfig)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			errorDict.update({res.ignore_indexes[i]: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(requestConfig.graphName, "insertNodesBulk", clientInfo.host, reTry, False)
		return uqlres

	def _batchInsertNodesBulk(self, insertReq: ULTIPA_REQUEST.InsertNodeBulk,
							  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> List[
		ULTIPA_RESPONSE.ResponseBulkInsert]:
		batchRetList = []
		if insertReq.batch:
			for some in [insertReq.rows[i:i + insertReq.n] for i in range(0, len(insertReq.rows), insertReq.n)]:
				batchReq = ULTIPA_REQUEST.InsertNodeBulk(insertReq.schema, some, insertReq.insertType,
														 insertReq.silent)
				ret = self._insertNodesBulk(batchReq, requestConfig)
				batchRetList.append(ret)
		return batchRetList

	def _insertEdgesBulk(self, insertReq: ULTIPA_REQUEST.InsertEdgeBulk,
						 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseBulkInsert:
		req = copy.deepcopy(insertReq)
		try:
			if requestConfig.graphName == '' and self.defaultConfig.defaultGraph != '':
				requestConfig.graphName = self.defaultConfig.defaultGraph
			clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=requestConfig.graphName)
			propertyRet = self.uql(GetPropertyBySchema.edge,
								   ULTIPA_REQUEST.RequestConfig(graphName=requestConfig.graphName))
			schemaDict = None
			if propertyRet.status.code == ULTIPA.Code.SUCCESS:
				for aliase in propertyRet.aliases:
					if aliase.alias == '_edgeSchema':
						schemaDict = convertTableToDict(propertyRet.alias(aliase.alias).data.rows,
														propertyRet.alias(aliase.alias).data.headers)
				if not schemaDict:
					raise ParameterException(err='Please create Edge Schema')
			else:
				raise ParameterException(err=propertyRet.status.message)
			# _edgeTable = FormatType.toEdgeTable(edgeSchamHeaders, req.rows)
			_edgeTable = FormatType.toEdgeTableSingle(schemaDict, req.schema, req.rows,
													  getTimeZoneOffset(requestConfig=insertReq,
																		defaultConfig=self.defaultConfig))
			edgeTable = ultipa_pb2.EdgeTable(schemas=_edgeTable.schemas, edge_rows=_edgeTable.edgeRows)
			request = ultipa_pb2.InsertEdgesRequest()
			request.silent = req.silent
			request.insert_type = req.insertType
			request.graph_name = requestConfig.graphName
			request.create_node_if_not_exist = req.create_node_if_not_exist
			request.edge_table.MergeFrom(edgeTable)
			res = clientInfo.Rpcsclient.InsertEdges(request, metadata=clientInfo.metadata)
		except Exception as e:
			errorRes = ULTIPA_RESPONSE.Response()
			try:
				message = str(e._state.code) + ' : ' + str(e._state.details)
			except:
				message = str(e)

			errorRes.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)
			errorRes.req = ULTIPA.ReturnReq(requestConfig.graphName, "insertEdgesBulk",
											requestConfig.useHost if requestConfig.useHost else self.host,
											requestConfig.retry,
											False)
			return errorRes
		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, requestConfig, uqlres)
		if reTry.canRetry:
			requestConfig.retry = reTry.nextRetry
			return self.insertEdgesBulk(req, requestConfig)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			errorDict.update({res.ignore_indexes[i]: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(requestConfig.graphName, "insertEdgesBulk", clientInfo.host, reTry, False)
		return uqlres

	def _batchInsertEdgesBulk(self, insertReq: ULTIPA_REQUEST.InsertEdgeBulk,
							  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> List[
		ULTIPA_RESPONSE.ResponseBulkInsert]:
		batchRetList = []
		if insertReq.batch:
			for some in [insertReq.rows[i:i + insertReq.n] for i in range(0, len(insertReq.rows), insertReq.n)]:
				batchReq = ULTIPA_REQUEST.InsertEdgeBulk(insertReq.schema, some, insertReq.insertType,
														 insertReq.silent)
				ret = self._insertEdgesBulk(batchReq, requestConfig)
				batchRetList.append(ret)
		return batchRetList

	# def clearTimeoutHandle(self):
	#     if self.timeoutHandle:
	#         clearInterval(this.timeoutHandle)
	#     self.timeoutHandle = null
	def stopConnectionAlive(self):
		if self.runSchedule != None:
			self.runSchedule.set()

	def keepConnectionAlive(self, timeIntervalSeconds: int = None):
		timeIntervalSeconds = self.defaultConfig.heartBeat if timeIntervalSeconds == None else timeIntervalSeconds

		def test_allconn():
			goGraphName = self.defaultConfig.defaultGraph
			for host in self.hostManagerControl.getAllClientInfos(goGraphName):
				res = host.Controlsclient.SayHello(ultipa_pb2.HelloUltipaRequest(name="test"),
												   metadata=host.getMetadata(goGraphName, None, None))
				# print(host.host,res.message)
				if self.defaultConfig.uqlLoggerConfig is None:
					self.defaultConfig.uqlLoggerConfig = LoggerConfig(name="HeartBeat", fileName=None,
																	  isWriteToFile=False,
																	  isStream=True)
				self.defaultConfig.uqlLoggerConfig.getlogger().info(f"HeartBeat:{host.host}--{res.message}")

		schedule.every().second.do(test_allconn)
		self.runSchedule = run_continuously(timeIntervalSeconds)

	## go
	def _InsertNodesBatch(self, nodeTable: ULTIPA_REQUEST.InsertNodeTable, config: ULTIPA_REQUEST.InsertConfig):

		config.useMaster = True
		if config.graphName == '' and self.defaultConfig.defaultGraph != '':
			config.graphName = self.defaultConfig.defaultGraph
		clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graphName,
										useMaster=config.useMaster)

		newNodetable = FormatType.serializeNodeTable(nodeTable)
		_nodeTable = ultipa_pb2.NodeTable(schemas=newNodetable.schemas, node_rows=newNodetable.nodeRows)
		request = ultipa_pb2.InsertNodesRequest()
		request.silent = config.silent
		request.insert_type = config.insertType
		request.graph_name = config.graphName
		request.node_table.MergeFrom(_nodeTable)
		res = clientInfo.Rpcsclient.InsertNodes(request, metadata=clientInfo.metadata)

		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, config, uqlres)
		if reTry.canRetry:
			config.retry = reTry.nextRetry
			return self._InsertNodesBatch(nodeTable, config)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			errorDict.update({res.ignore_indexes[i]: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(config.graphName, "InsertNodesBatch", clientInfo.host, reTry, False)
		return uqlres

	def _InsertEdgesBatch(self, edgeTable: ULTIPA_REQUEST.InsertEdgeTable, config: ULTIPA_REQUEST.InsertConfig):

		config.useMaster = True
		if config.graphName == '' and self.defaultConfig.defaultGraph != '':
			config.graphName = self.defaultConfig.defaultGraph
		clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graphName,
										useMaster=config.useMaster)

		newEdgetable = FormatType.serializeEdgeTable(edgeTable)
		_nodeTable = ultipa_pb2.EdgeTable(schemas=newEdgetable.schemas, edge_rows=newEdgetable.edgeRows)
		request = ultipa_pb2.InsertEdgesRequest()
		request.silent = config.silent
		request.insert_type = config.insertType
		request.graph_name = config.graphName
		request.edge_table.MergeFrom(_nodeTable)
		res = clientInfo.Rpcsclient.InsertEdges(request, metadata=clientInfo.metadata)

		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, config, uqlres)
		if reTry.canRetry:
			config.retry = reTry.nextRetry
			return self._InsertEdgesBatch(edgeTable, config)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			errorDict.update({res.ignore_indexes[i]: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(config.graphName, "InsertEdgesBatch", clientInfo.host, reTry, False)
		return uqlres

	def insertNodesBatchBySchema(self, schema: ULTIPA_REQUEST.Schema, rows: List[ULTIPA.EntityRow],
								 config: ULTIPA_REQUEST.InsertConfig) -> ULTIPA_RESPONSE.InsertResponse:
		config.useMaster = True
		if config.graphName == '' and self.defaultConfig.defaultGraph != '':
			config.graphName = self.defaultConfig.defaultGraph

		clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graphName,
										useMaster=config.useMaster)

		nodetable = FormatType.makeEntityNodeTable(schema, rows, getTimeZoneOffset(requestConfig=config,
																				   defaultConfig=self.defaultConfig))

		_nodeTable = ultipa_pb2.EntityTable(schemas=nodetable.schemas, entity_rows=nodetable.nodeRows)
		request = ultipa_pb2.InsertNodesRequest()
		request.silent = config.silent
		request.insert_type = config.insertType
		request.graph_name = config.graphName
		request.node_table.MergeFrom(_nodeTable)
		res = clientInfo.Rpcsclient.InsertNodes(request, metadata=clientInfo.metadata)

		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, config, uqlres)
		if reTry.canRetry:
			config.retry = reTry.nextRetry
			return self.insertNodesBatchBySchema(schema, rows, config)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			try:
				index = rows[res.ignore_indexes[i]]._getIndex()
			except Exception as e:
				try:
					index = res.ignore_indexes[i]
				except Exception as e:
					index = i
			if index is None:
				try:
					index = res.ignore_indexes[i]
				except Exception as e:
					index = i
			errorDict.update({index: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(config.graphName, "InsertNodesBatchBySchema", clientInfo.host, reTry,
										  False)
		return uqlres

	def insertEdgesBatchBySchema(self, schema: ULTIPA_REQUEST.Schema, rows: List[ULTIPA.EntityRow],
								 config: ULTIPA_REQUEST.InsertConfig) -> ULTIPA_RESPONSE.InsertResponse:
		config.useMaster = True
		if config.graphName == '' and self.defaultConfig.defaultGraph != '':
			config.graphName = self.defaultConfig.defaultGraph

		clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graphName,
										useMaster=config.useMaster)

		edgetable = FormatType.makeEntityEdgeTable(schema=schema, rows=rows,
												   timeZoneOffset=getTimeZoneOffset(requestConfig=config,
																					defaultConfig=self.defaultConfig))

		_edgeTable = ultipa_pb2.EntityTable(schemas=edgetable.schemas, entity_rows=edgetable.edgeRows)
		request = ultipa_pb2.InsertEdgesRequest()
		request.silent = config.silent
		request.insert_type = config.insertType
		request.graph_name = config.graphName
		request.create_node_if_not_exist = config.createNodeIfNotExist
		request.edge_table.MergeFrom(_edgeTable)
		res = clientInfo.Rpcsclient.InsertEdges(request, metadata=clientInfo.metadata)

		status = FormatType.status(res.status)
		uqlres = ULTIPA_RESPONSE.Response(status=status)
		# 验证是否要跳转
		reTry = RetryHelp.check(self, config, uqlres)
		if reTry.canRetry:
			config.retry = reTry.nextRetry
			return self.insertEdgesBatchBySchema(schema, rows, config)

		uRes = ULTIPA_RESPONSE.ResponseBulk()
		uRes.uuids = [i for i in res.uuids]
		errorDict = {}
		for i, data in enumerate(res.ignore_error_code):
			try:
				index = rows[res.ignore_indexes[i]]._getIndex()
			except Exception as e:
				try:
					index = res.ignore_indexes[i]
				except Exception as e:
					index = i
			if index is None:
				try:
					index = res.ignore_indexes[i]
				except Exception as e:
					index = i
			errorDict.update({index: data})
		uRes.errorItem = errorDict
		uqlres.data = uRes
		uqlres.total_time = res.time_cost
		uqlres.engine_time = res.engine_time_cost
		if self.defaultConfig.responseWithRequestInfo:
			uqlres.req = ULTIPA.ReturnReq(config.graphName, "InsertEdgesBatchBySchema", clientInfo.host, reTry,
										  False)
		return uqlres

	def insertNodesBatchAuto(self, nodes: List[ULTIPA.EntityRow],
							 config: ULTIPA_REQUEST.InsertConfig) -> ULTIPA_RESPONSE.ResponseBatchAutoInsert:
		Result = {}
		schemaDict = {}
		batches = {}
		schemaRet = self.uql(GetPropertyBySchema.node, config)
		if schemaRet.status.code == ULTIPA.Code.SUCCESS:
			for aliase in schemaRet.aliases:
				if aliase.alias == '_nodeSchema':
					schemaDict = convertTableToDict(schemaRet.alias(aliase.alias).data.rows,
													schemaRet.alias(aliase.alias).data.headers)
			if not schemaDict:
				raise ParameterException(err='Please create Node Schema.')
		else:
			raise ParameterException(err=schemaRet.status.message)
		for index, node in enumerate(nodes):
			node._index = index
			if batches.get(node.schema) is None:
				batches[node.schema] = ULTIPA_REQUEST.Batch()
				find = list(filter(lambda x: x.get('name') == node.schema, schemaDict))
				if find:
					findSchema = find[0]
					propertyList = FormatType.checkProperty(node, json.loads(findSchema.get("properties")))
					reqSchema = ULTIPA_REQUEST.Schema(node.schema, propertyList)
					batches[node.schema].Schema = reqSchema
				else:
					if node.schema is None:
						raise ParameterException(err=f"Row [{index}]:Please set schema name for node.")
					else:
						raise ParameterException(err=f"Row [{index}]:Node Schema not found {node.schema}.")

			batches.get(node.schema).Nodes.append(node)
		for key in batches:
			batch = batches.get(key)
			Result.update({key: self.insertNodesBatchBySchema(schema=batch.Schema, rows=batch.Nodes, config=config)})

		newStatusMsg = ""
		newCode = None
		for i, key in enumerate(Result):
			ret = Result.get(key)
			newStatusMsg += f"{key}:{ret.status.message} "
			if ret.status.code != ULTIPA.Code.SUCCESS and not newCode:
				newCode = ret.status.code
		if newCode is None:
			newCode = ULTIPA.Code.SUCCESS
		status = ULTIPA_RESPONSE.Status(newCode, newStatusMsg)
		newResponse = ULTIPA_RESPONSE.ResponseBatchAutoInsert(status=status)
		newResponse.data = Result
		return newResponse

	def insertEdgesBatchAuto(self, edges: List[ULTIPA.EntityRow],
							 config: ULTIPA_REQUEST.InsertConfig) -> ULTIPA_RESPONSE.ResponseBatchAutoInsert:
		Result = {}
		schemaDict = []
		batches = {}
		schemaRet = self.uql(GetPropertyBySchema.edge, config)
		if schemaRet.status.code == ULTIPA.Code.SUCCESS:
			for aliase in schemaRet.aliases:
				if aliase.alias == '_edgeSchema':
					schemaDict = convertTableToDict(schemaRet.alias(aliase.alias).data.rows,
													schemaRet.alias(aliase.alias).data.headers)
			if not schemaDict:
				raise ParameterException(err='Please create Edge Schema.')
		else:
			raise ParameterException(err=schemaRet.status.message)
		for index, edge in enumerate(edges):
			edge._index = index
			if batches.get(edge.schema) == None:
				batches[edge.schema] = ULTIPA_REQUEST.Batch()
				find = list(filter(lambda x: x.get('name') == edge.schema, schemaDict))
				if find:
					findSchema = find[0]
					propertyList = FormatType.checkProperty(edge, json.loads(findSchema.get("properties")))
					reqSchema = ULTIPA_REQUEST.Schema(edge.schema, propertyList)
					batches[edge.schema].Schema = reqSchema
				else:
					if edge.schema is None:
						raise ParameterException(err=f"Row [{index}]:Please set schema name for edge.")
					else:
						raise ParameterException(err=f"Row [{index}]:Edge Schema not found {edge.schema}.")
			batches.get(edge.schema).Edges.append(edge)
		for key in batches:
			batch = batches.get(key)
			Result.update({key: self.insertEdgesBatchBySchema(schema=batch.Schema, rows=batch.Edges, config=config)})

		newStatusMsg = ""
		newCode = None
		for i, key in enumerate(Result):
			ret = Result.get(key)
			newStatusMsg += f"{key}:{ret.status.message} "
			if ret.status.code != ULTIPA.Code.SUCCESS and not newCode:
				newCode = ret.status.code
		if newCode is None:
			newCode = ULTIPA.Code.SUCCESS
		status = ULTIPA_RESPONSE.Status(newCode, newStatusMsg)
		newResponse = ULTIPA_RESPONSE.ResponseBatchAutoInsert(status=status)
		newResponse.data = Result
		return newResponse

	def _InsertByCSV(self, csvPath: str, type: ULTIPA.DBType, config: ULTIPA_REQUEST.InsertConfig,
					 schemaName: str = None) -> ULTIPA_RESPONSE.ResponseBatchAutoInsert:
		rows = []
		propertyType = []
		properties = []
		types = []
		with open(csvPath, "r", encoding="utf-8-sig") as csvfile:
			reader = csv.reader(csvfile)
			for i, line in enumerate(reader):
				if i == 0:
					for i, property in enumerate(line):
						k1, k2 = property.split(":")
						propertyType.append({k1: k2})
						types.append({"index": i, "type": k2})
						properties.append(k1)
					continue
				for i in types:
					if i.get("type") in ["int", "int32", "int64"]:
						if line[i.get("index")] == "":
							line[i.get("index")] = 0
							continue
						line[i.get("index")] = int(line[i.get("index")])
					if i.get("type") in ["float", "double"]:
						if line[i.get("index")] == "":
							line[i.get("index")] = 0.0
							continue
						line[i.get("index")] = float(line[i.get("index")])
				line = dict(zip(properties, line))
				if i == 0:
					print(line.keys())
				if type == ULTIPA.DBType.DBNODE:
					if line.get("_uuid"):
						uuid = line.get("_uuid")
						line.__delitem__("_uuid")
						rows.append(ULTIPA.Node(line, schema_name=schemaName, uuid=int(uuid)))
					elif line.get("_id"):
						id = line.get("_id")
						line.__delitem__("_id")
						rows.append(ULTIPA.Node(line, schema_name=schemaName, id=id))
					else:
						rows.append(ULTIPA.Node(line, schema_name=schemaName))

				elif type == ULTIPA.DBType.DBEDGE:
					if line.get("_from_uuid") and line.get("_to_uuid"):
						from_uuid = line.get("_from_uuid")
						line.__delitem__("_from_uuid")
						to_uuid = line.get("_to_uuid")
						line.__delitem__("_to_uuid")
						line.__delitem__("_id")
						rows.append(
							ULTIPA.Edge(line, schema_name=schemaName, from_uuid=int(from_uuid), to_uuid=int(to_uuid)))
					elif line.get("_from_id") and line.get("_to_id"):
						from_id = line.get("_from_id")
						line.__delitem__("_from_id")
						to_id = line.get("_to_id")
						line.__delitem__("_to_id")
						if line.get("_id"):
							line.__delitem__("_id")
						rows.append(ULTIPA.Edge(line, schema_name=schemaName, from_id=from_id, to_id=to_id))

		if type == ULTIPA.DBType.DBNODE:
			return self.insertNodesBatchAuto(rows, config)
		else:
			return self.insertEdgesBatchAuto(rows, config)
