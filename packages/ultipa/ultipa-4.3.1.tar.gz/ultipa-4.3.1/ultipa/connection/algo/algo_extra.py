import hashlib
import os
from hashlib import md5

from ultipa.connection.algo import ALGO_REQUEST
from ultipa.connection.connection_base import ConnectionBase
from ultipa.proto import ultipa_pb2
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList, errors
from ultipa.utils.fileSize import read_in_chunks
from ultipa.utils.format import FormatType
from ultipa.utils.ResposeFormat import ResponseKeyFormat


class ALGO_RESULT:
	ALGO_RESULT_UNSET = -1
	WRITE_TO_FILE = 1
	WRITE_TO_DB = 2
	WRITE_TO_CLIENT = 4
	WRITE_TO_VISUALIZATION = 8


class AlgoExtra(ConnectionBase):
	JSONSTRING_KEYS = ["param"]

	def showAlgo(self,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListAlgo:
		uqlMaker = UQLMAKER(command=CommandList.showAlgo, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(jsonKeys=self.JSONSTRING_KEYS))
		if res.status.code == ULTIPA.Code.SUCCESS:
			for algo in res.data:
				try:
					result_opt = int(algo.param.get("result_opt", 0))
				except Exception as e:
					raise errors.ParameterException(e)
				result_opt_obj = ULTIPA_RESPONSE.AlgoResultOpt()
				result_opt_obj.can_realtime = True if result_opt & ALGO_RESULT.WRITE_TO_CLIENT else False
				result_opt_obj.can_visualization = True if result_opt & ALGO_RESULT.WRITE_TO_VISUALIZATION else False
				result_opt_obj.can_write_back = True if result_opt & (
						ALGO_RESULT.WRITE_TO_DB | ALGO_RESULT.WRITE_TO_FILE) else False
				algo.__setattr__("result_opt", result_opt_obj)
		return res

	# def algo_dv(self,request: ALGO_REQUEST.Dv,requestConfig:ULTIPA_REQUEST.RequestConfig =ULTIPA_REQUEST.RequestConfig()) ->  ULTIPA_RESPONSE.Response:
	#     uqlMaker = UQLMAKER(command=CommandList.algo_dv, commandP=request.algo_name,commonParams=requestConfig)
	#     uqlMaker.addParam('id',request.id)
	#     uqlMaker.addParam('params',{'top':request.top,'total':request.total})
	#     res = self.uqlSingle(uqlMaker)
	#     return res

	# @staticmethod
	# def algoCommonSend(conn: ConnectionBase, algo_name: str, request: ALGO_REQUEST.AlgoBaseModel,
	# 				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
	# 	algo_name = algo_name.replace('algo_', '')
	# 	uqlMaker = UQLMAKER(command=CommandList.algo, commandP=algo_name, commonParams=requestConfig)
	#
	# 	if request.toDict():
	# 		req = request.toDict()
	# 		req_dict = {}
	# 		for (k, v) in req.items():
	# 			if k not in ['write', 'visualization', 'force', 'realtime', 'filename1', 'filename2',
	# 						 'property'] and v != None:
	# 				req_dict.update({k: v})
	# 		uqlMaker.addParam('params', req_dict)
	#
	# 	if request.write:
	# 		if request.filename1 != None:
	# 			if request.filename2 != None:
	# 				value = ".write({file: {filename1:\"request.filename1\",filename2:\"request.filename2\"}})"
	# 			else:
	# 				value = ".write({file: {filename1:\"request.filename1\"}})"
	# 		else:
	# 			value = ""
	# 		if request.property != None:
	# 			value = ".write({db: {property:\"request.property\"}})"
	# 		else:
	# 			value = ""
	#
	# 		uqlMaker.addParam('write', value=value, required=False)
	#
	# 	if request.visualization:
	# 		uqlMaker.addParam('visualization', value='', required=False)
	#
	# 	if request.force:
	# 		uqlMaker.addParam('force', value='', required=False)
	#
	# 	res = conn.uqlSingle(uqlMaker)
	# 	return res

	def __make_message(self, filename, md5, chunk):
		return ultipa_pb2.InstallAlgoRequest(
			file_name=filename, md5=md5, chunk=chunk
		)

	def __generate_messages(self, request: ULTIPA_REQUEST.InstallAlgo):
		messages = []
		file_object = open(request.soPath, 'rb')
		somd5 = hashlib.md5(file_object.read()).hexdigest()
		file_object.close()

		for chunk in read_in_chunks(request.soPath):
			filename = os.path.basename(request.soPath)
			messages.append(self.__make_message(filename, somd5, chunk))

		file_object = open(request.configPath, 'rb')
		configmd5 = hashlib.md5(file_object.read()).hexdigest()
		file_object.close()
		for chunk in read_in_chunks(request.configPath):
			filename = os.path.basename(request.configPath)
			messages.append(self.__make_message(filename, configmd5, chunk))
		for msg in messages:
			yield msg

	def installAlgo(self, request: ULTIPA_REQUEST.InstallAlgo,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		requestConfig.useMaster = True
		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster,isGlobal=True)
		response = ULTIPA_RESPONSE.Response()
		try:
			if os.path.exists(request.soPath) and os.path.exists(request.configPath):
				installRet = clientInfo.Controlsclient.InstallAlgo(self.__generate_messages(request),
																   metadata=clientInfo.metadata)
				status = FormatType.status(installRet.status)
				response.status = status
		except Exception as e:
			try:
				message = str(e._state.code) + ' : ' + str(e._state.details)
			except:
				message = str(e)

			response.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)

		if self.defaultConfig.responseWithRequestInfo:
			response.req = ULTIPA.ReturnReq(self.graphSetName, "InstallAlgo",
											requestConfig.useHost if requestConfig.useHost else self.host, requestConfig.retry,
											False)
		return response

	def uninstallAlgo(self, request: ULTIPA_REQUEST.UninstallAlgo,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		requestConfig.useMaster=True
		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster,isGlobal=True)
		arequest = ultipa_pb2.UninstallAlgoRequest(algo_name=request.algoName)
		installRet = clientInfo.Controlsclient.UninstallAlgo(arequest, metadata=clientInfo.metadata)
		status = FormatType.status(installRet.status)
		response = ULTIPA_RESPONSE.Response(status=status)
		if self.defaultConfig.responseWithRequestInfo:
			response.req = ULTIPA.ReturnReq(self.graphSetName, "InstallAlgo",
											requestConfig.useHost if requestConfig.useHost else self.host, requestConfig.retry,
											False)
		return response

	def installExtaAlgo(self, request: ULTIPA_REQUEST.InstallExtaAlgo,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		requestConfig.useMaster = True
		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster)
		response = ULTIPA_RESPONSE.Response()
		try:
			if os.path.exists(request.soPath) and os.path.exists(request.configPath):
				installRet = clientInfo.Controlsclient.InstallExta(self.__generate_messages(request),
																   metadata=clientInfo.metadata)
				status = FormatType.status(installRet.status)
				response.status = status
		except Exception as e:
			try:
				message = str(e._state.code) + ' : ' + str(e._state.details)
			except:
				message = str(e)

			response.status = ULTIPA.Status(code=ULTIPA.Code.UNKNOW_ERROR, message=message)

		if self.defaultConfig.responseWithRequestInfo:
			response.req = ULTIPA.ReturnReq(self.graphSetName, "InstallAlgo",
											requestConfig.useHost if requestConfig.useHost else self.host,
											requestConfig.retry,
											False)
		return response

	def uninstallExtaAlgo(self, request: ULTIPA_REQUEST.UninstallExtaAlgo,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.Response:
		requestConfig.useMaster = True
		clientInfo = self.getClientInfo(graphSetName=requestConfig.graphName, useMaster=requestConfig.useMaster)
		arequest = ultipa_pb2.UninstallExtaRequest(exta_name=request.algoName)
		installRet = clientInfo.Controlsclient.UninstallExta(arequest, metadata=clientInfo.metadata)
		status = FormatType.status(installRet.status)
		response = ULTIPA_RESPONSE.Response(status=status)
		if self.defaultConfig.responseWithRequestInfo:
			response.req = ULTIPA.ReturnReq(self.graphSetName, "InstallAlgo",
											requestConfig.useHost if requestConfig.useHost else self.host,
											requestConfig.retry,
											False)
		return response



