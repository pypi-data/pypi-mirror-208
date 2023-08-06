from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
from ultipa.utils import UQLMAKER, CommandList


class EdgeExtra(ConnectionBase):

	def searchEdge(self, request: ULTIPA_REQUEST.SearchEdge,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseSearchEdge:
		'''
		:EXP: conn.searchEdge(ULTIPA_REQUEST.SearchMate(id='1',select=['name']))
		:param request: ULTIPA_REQUEST
		:param requestConfig:
		:return:
		'''
		uqlMaker = UQLMAKER(command=CommandList.edges, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)

		uqlMaker.addParam('as', request.select.aliasName)
		uqlMaker.addParam("return", request.select)

		# uqlMaker.addParam("limit", request.limit)

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
		# uqlReply = res.data
		# if len(uqlReply.edges) > 0:
		#     res.data = res.data.edges[0].edges
		# else:
		#     res.data=uqlReply.edges
		return res

	def insertEdge(self, request: ULTIPA_REQUEST.InsertEdge,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseInsert:
		'''
		:param requestConfig:
		:EXP: conn.insertEdge(ULTIPA_REQUEST.InsertEdge(edges=[{'_from_id':1,'_to_id':2,'name':'TestEdge'}]))
		:param request: ULTIPA_REQUEST
		:return: status
		'''
		uqlMaker = UQLMAKER(command=CommandList.insert, commonParams=requestConfig)
		if request.upsert:
			uqlMaker = UQLMAKER(command=CommandList.upsert, commonParams=requestConfig)
		if request.overwrite:
			uqlMaker.addParam('overwrite', "", required=False)
		if request.schemaName:
			uqlMaker.addParam('into', request.schemaName, required=False)
		uqlMaker.addParam('edges', request.edges)

		if request.isReturnID:
			uqlMaker.addParam('as', "edges")
			uqlMaker.addParam('return', "edges._uuid")
		res = self.uqlSingle(uqlMaker)
		if res.status.code != ULTIPA.Code.SUCCESS:
			return res
		if request.isReturnID:
			if len(res.aliases) > 0:
				res.data = res.items.get(res.aliases[0].alias).data
		return res

	def updateEdge(self, request: ULTIPA_REQUEST.UpdateEdge,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:EXP: conn.updateEdge(ULTIPA_REQUEST.UpdateMate(id='1',params={'rank':30}))
		:param request: ULTIPA_REQUEST
		:param requestConfig:
		:return: status
		'''
		uqlMaker = UQLMAKER(command=CommandList.updateEdges, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)
		uqlMaker.addParam("set", request.values)
		uqlMaker.addParam("silent", request.silent)
		res = self.UqlUpdateSimple(self, uqlMaker)
		return res

	def deleteEdge(self, request: ULTIPA_REQUEST.DeleteEdge,
				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.UltipaResponse:
		'''
		:param requestConfig:
		:EXP: conn.deleteEdge(ULTIPA_REQUEST.DeleteMate(filter={'name':'TestEdge'}))
		:param request: ULTIPA_REQUEST
		:return: status
		'''
		uqlMaker = UQLMAKER(command=CommandList.deleteEdges, commonParams=requestConfig)
		if request.id:
			uqlMaker.setCommandParams(request.id)
		elif request.filter:
			uqlMaker.setCommandParams(request.filter)
		res = self.UqlUpdateSimple(self, uqlMaker)
		return res
