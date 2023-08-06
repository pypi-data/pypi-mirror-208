import json

from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA, ULTIPA_REQUEST, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList

# BOOL_KEYS = ["index","lte"]
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.propertyUtils import getPropertyTypesDesc

BOOL_KEYS = ["index", "lte"]
REPLACE_KEYS = {
	"name": "propertyName",
	"type": "propertyType",
}


class PropertyExtra(ConnectionBase):

	def listProperty(self,requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListProperty:
		return self.showProperty(requestConfig)

	def showProperty(self,requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseListProperty:
		command = CommandList.showProperty
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS, boolKeys=BOOL_KEYS),
								 isSingleOne=False)
		return res

	def getProperty(self, request: ULTIPA_REQUEST.GetProperty,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseGetProperty:
		'''
		:EXP: conn.listProperty(ULTIPA_REQUEST.GetProperty(type=ULTIPA.DBType.DBNODE))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		if request:
			if request.type == ULTIPA.DBType.DBNODE:
				command = CommandList.showNodeProperty
			elif request.type == ULTIPA.DBType.DBEDGE:
				command = CommandList.showEdgeProperty
			else:
				command = CommandList.showNodeProperty
			if request.schemaName:
				commandp = ['@' + request.schemaName]
			else:
				commandp = ''
		else:
			command = CommandList.showNodeProperty
			commandp = ''

		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commandp)
		res = self.UqlListSimple(self, uqlMaker=uqlMaker,
								 responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS, boolKeys=BOOL_KEYS),
								 isSingleOne=False)
		if res.data!=None and len(res.data) > 0:
			res.data = res.data[0].data
		return res


	def createProperty(self, request: ULTIPA_REQUEST.CreateProperty,
					   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.createProperty(ULTIPA_REQUEST.CreatProperty(type=ULTIPA.DBType.DBNODE, name='test_int',property_type=ULTIPA.CreatePropertyType.PROPERTY_INT))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.createNodeProperty or CommandList.createEdgeProperty
		commandP = [request.schemaName.schemaName, request.schemaName.propertyName, getPropertyTypesDesc(request.propertyType,request.subTypes)]

		if request.description:
			commandP.append(request.description)
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commandP)
		# res = self.UqlUpdateSimple(self, uqlMaker=uqlMaker)
		res = self.uqlSingle(uqlMaker)
		return res

	def dropProperty(self, request: ULTIPA_REQUEST.DropProperty,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.dropProperty(ULTIPA_REQUEST.DropProperty(type=ULTIPA.DBType.DBNODE, name='test'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.dropNodeProperty or CommandList.dropEdgeProperty
		commandP = request.schemaName.toString
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP=commandP)
		res = self.uqlSingle(uqlMaker)
		return res

	def alterProperty(self, request: ULTIPA_REQUEST.AlterProperty,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.alterProperty(ULTIPA_REQUEST.DropProperty(type=ULTIPA.DBType.DBNODE, name='test'))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		command = request.type == ULTIPA.DBType.DBNODE and CommandList.alterNodeProperty or CommandList.alterEdgeProperty
		commandP = request.schemaName.toString
		update_dict = {}
		if request.new_name:
			update_dict.setdefault('name', request.new_name)
		if request.description:
			update_dict.update({'description': request.description})
		uqlMaker = UQLMAKER(command=command, commonParams=requestConfig)
		uqlMaker.setCommandParams(commandP)
		uqlMaker.addParam("set", update_dict)
		res = self.uqlSingle(uqlMaker)
		return res
