from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList


class NodeExtra(ConnectionBase):

	def searchNode(self, request: ULTIPA_REQUEST.SearchNode,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseSearchNode:
		'''
		:param requestConfig:
		:EXP: conn.searchNode(ULTIPA_REQUEST.SearchMate(id='1',select=['name']))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.nodes, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)
		uqlMaker.addParam('as', request.select.aliasName)
		uqlMaker.addParam("return", request.select)
		# if request.skip:
		#     uqlMaker.addParam("skip", request.skip)
		#
		# if hasattr(request, 'order_by'):
		#     uqlMaker.addParam("order_by", request.order_by)
		#
		# if hasattr(request, 'group_by'):
		#     uqlMaker.addParam("group_by", request.group_by)

		res = self.uqlSingle(uqlMaker)
		if res.status.code != ULTIPA.Code.SUCCESS:
			return res

		return res

	def insertNode(self, request: ULTIPA_REQUEST.InsertNode,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseInsert:
		'''
		:param requestConfig:
		:EXP: conn.insertNode(ULTIPA_REQUEST.InsertNode(nodes=[{'name':'test'},{'name':'test2'}]))
		:param request: ULTIPA_REQUEST
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.insert, commonParams=requestConfig)
		if request.upsert:
			uqlMaker = UQLMAKER(command=CommandList.upsert, commonParams=requestConfig)
		if request.overwrite:
			uqlMaker.addParam('overwrite', "", required=False)
		if request.schemaName:
			uqlMaker.addParam('into', request.schemaName, required=False)

		uqlMaker.addParam('nodes', request.nodes)

		if request.isReturnID:
			uqlMaker.addParam('as', "nodes")
			uqlMaker.addParam('return', "nodes._uuid")

		res = self.uqlSingle(uqlMaker)
		if res.status.code != ULTIPA.Code.SUCCESS:
			return res
		if request.isReturnID:
			if len(res.aliases) > 0:
				res.data = res.items.get(res.aliases[0].alias).data
		return res

	def updateNode(self, request: ULTIPA_REQUEST.UpdateNode,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.updateNode(ULTIPA_REQUEST.UpdateMate(id='1',params={'age':30}))
		:param request: ULTIPA_REQUEST
		:param requestConfig:
		:return: status
		'''
		uqlMaker = UQLMAKER(command=CommandList.updateNodes, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)
		uqlMaker.addParam("set", request.values)
		uqlMaker.addParam("silent", request.silent)
		res = self.uqlSingle(uqlMaker)
		return res

	def deleteNode(self, request: ULTIPA_REQUEST.DeleteNode,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.deleteNode(ULTIPA_REQUEST.DeleteMate(filter={'name':'test'}))
		:param request: ULTIPA_REQUEST
		:return: status
		'''
		uqlMaker = UQLMAKER(command=CommandList.deleteNodes, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)
		res = self.uqlSingle(uqlMaker)
		return res
