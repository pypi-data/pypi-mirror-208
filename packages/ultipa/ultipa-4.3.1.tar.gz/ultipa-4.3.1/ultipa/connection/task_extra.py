from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList
import json

from ultipa.utils.convert import convertToAnyObject
from ultipa.utils.ResposeFormat import ResponseKeyFormat


class ALGO_RETURN_TYPE:
	ALGO_RETURN_REALTIME = 1
	ALGO_RETURN_WRITE_BACK = 2
	ALGO_RETURN_VISUALIZATION = 4


class TaskExtra(ConnectionBase):

	def top(self,
			requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListTop:
		uqlMaker = UQLMAKER(command=CommandList.top, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker)
		return res

	def kill(self, request: ULTIPA_REQUEST.Kill,
			 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		commonP = []
		if request.id:
			commonP = request.id
		if request.all:
			commonP = '*'
		uqlMaker = UQLMAKER(command=CommandList.kill, commonParams=requestConfig)
		uqlMaker.setCommandParams(commonP)
		res = self.uqlSingle(uqlMaker)
		return res

	def showTask(self, request: ULTIPA_REQUEST.ShowTask,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListTask:
		'''
		:EXP: conn.showTask(ULTIPA_REQUEST.ShowTask(limit=10))
		:param req: ULTIPA_REQUEST
		:return:
		'''
		_jsonKeys = ['taskJson']
		uqlMaker = UQLMAKER(command=CommandList.showTask, commonParams=requestConfig)
		commonP = []
		if request.name and request.status:
			commonP.append(request.name)
			commonP.append(request.status)
		if request.name and not request.status:
			commonP.append(request.name)
			commonP.append('*')
		if not request.name and request.status:
			commonP.append('*')
			commonP.append(request.status)
		if request.id:
			commonP = request.id
		uqlMaker.setCommandParams(commandP=commonP)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(jsonKeys=_jsonKeys))
		newDatas = []
		if res.data:
			for obj in res.data:
				obj = obj.__dict__
				newData = ULTIPA_RESPONSE.Task()
				taskJson = obj.get("taskJson", {})
				newData.param = json.loads(taskJson.get("param", "{}"))
				newData.result = taskJson.get("result")
				task_info = taskJson.get("task_info", {})

				if task_info.get('status_code'):
					task_info["status_code"] = ULTIPA.TaskStatusString[task_info.get("TASK_STATUS")]
				if task_info.get('engine_cost'):
					task_info["engine_cost"] = task_info.get("writing_start_time", 0) - task_info.get("start_time", 0)

				newData.task_info = convertToAnyObject(task_info)
				return_type_get = int(task_info.get('return_type', 0))
				return_type = ULTIPA_RESPONSE.Return_Type()
				return_type.is_realtime = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_REALTIME else False
				return_type.is_visualization = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_VISUALIZATION else False
				return_type.is_wirte_back = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_WRITE_BACK else False
				newData.task_info.__setattr__('return_type', return_type)
				newDatas.append(newData)
			res.data = newDatas
		return res

	def clearTask(self, request: ULTIPA_REQUEST.ClearTask,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		'''
		:EXP: conn.clearTask(ULTIPA_REQUEST.ClearTask(id=['1'],name='out_degree'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.clearTask, commonParams=requestConfig)
		commonP = []
		if request.all:
			commonP.append('*')
		else:

			if request.name and request.status:
				commonP.append(request.name)
				commonP.append(request.status)
			if request.name and not request.status:
				commonP.append(request.name)
				commonP.append('*')
			if not request.name and request.status:
				commonP.append('*')
				commonP.append(request.status)
			if request.id:
				commonP = request.id

		uqlMaker.setCommandParams(commandP=commonP)
		res = self.UqlUpdateSimple(self, uqlMaker)

		return res

	# def pauseTask(self,request:ULTIPA_REQUEST.PauseTask,requestConfig:ULTIPA_REQUEST.RequestConfig =ULTIPA_REQUEST.RequestConfig())->ULTIPA_RESPONSE.ResponseCommon:
	#     uqlMaker = UQLMAKER(command=CommandList.pauseTask, commonParams=requestConfig)
	#     commonP = []
	#     if request.all:
	#         commonP = '*'
	#     if request.id:
	#         commonP = request.id
	#     uqlMaker.setCommandParams(commandP=commonP)
	#     return self.UqlUpdateSimple(self,uqlMaker)
	#
	# def resumeTask(self,request:ULTIPA_REQUEST.ResumeTask,requestConfig:ULTIPA_REQUEST.RequestConfig =ULTIPA_REQUEST.RequestConfig())->ULTIPA_RESPONSE.ResponseCommon:
	#     uqlMaker = UQLMAKER(command=CommandList.resumeTask,commonParams=requestConfig)
	#     commonP = []
	#     if request.all:
	#         commonP = '*'
	#     if request.id:
	#         commonP = request.id
	#     uqlMaker.setCommandParams(commandP=commonP)
	#     return self.UqlUpdateSimple(self,uqlMaker)

	def stopTask(self, request: ULTIPA_REQUEST.StopTask,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseCommon:
		uqlMaker = UQLMAKER(command=CommandList.stopTask, commonParams=requestConfig)
		commonP = []
		if request.all:
			commonP = '*'
		if request.id:
			commonP = request.id
		uqlMaker.setCommandParams(commandP=commonP)
		return self.UqlUpdateSimple(self, uqlMaker)

	def clusterInfo(self,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ClusterInfo:
		self.refreshRaftLeader(redirectHost='', requestConfig=requestConfig)
		result = []
		if not requestConfig.graphName:
			graphSetName = 'default'
		else:
			graphSetName = requestConfig.graphName
		for peer in self.hostManagerControl.getAllHostStatusInfo(graphSetName):
			info = ULTIPA_RESPONSE.Cluster()
			info.status = peer.status
			info.host = peer.host
			info.isLeader = peer.isLeader
			info.isFollowerReadable = peer.isFollowerReadable
			info.isAlgoExecutable = peer.isAlgoExecutable
			info.isUnset = peer.isUnset
			info.cpuUsage = None
			info.memUsage = None
			if peer.status:
				ret = self.stats(requestConfig=ULTIPA_REQUEST.RequestConfig(host=peer.host))
				if ret.status.code == ULTIPA.Code.SUCCESS:
					info.cpuUsage = ret.data.cpuUsage
					info.memUsage = ret.data.memUsage

			result.append(info)
		res = ULTIPA_RESPONSE.Response()
		res.data = result
		return res
