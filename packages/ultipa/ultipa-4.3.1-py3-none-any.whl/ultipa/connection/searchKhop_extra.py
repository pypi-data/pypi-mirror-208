# from ultipa.connection.connection_base import ConnectionBase
# from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
# from ultipa.utils import UQLMAKER, CommandList
#
#
# class SearchKhopExtra(ConnectionBase):
#
# 	def searchKhop(self, request: ULTIPA_REQUEST.Searchkhop,
# 				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseSearchKhop:
# 		'''
# 		:EXP: conn.searchKhop(ULTIPA_REQUEST.Searchkhop(src='12',depth=3,limit=5,select=['*']))
# 		:param req: ULTIPA_REQUEST
# 		:return:
# 		'''
# 		uqlMaker = UQLMAKER(command=CommandList.khop, commonParams=requestConfig)
# 		request.osrc and uqlMaker.addParam("osrc", request.osrc) or uqlMaker.addParam("src", request.src)
# 		uqlMaker.addParam("depth", request.depth)
# 		uqlMaker.addParam("limit", request.limit)
# 		uqlMaker.addParam("node_filter", request.node_filter)
# 		uqlMaker.addParam("edge_filter", request.edge_filter)
# 		uqlMaker.addParam("select", request.select)
# 		uqlMaker.addParam("select_node_properties", request.select_node_properties)
# 		uqlMaker.addParam("select_edge_properties", request.select_edge_properties)
# 		uqlMaker.addParam("direction", request.direction)
# 		uqlMaker.addParam("turbo", request.turbo)
# 		res = self.uqlSingle(uqlMaker)
# 		if res.status.code != ULTIPA.Code.SUCCESS:
# 			return res
# 		newData = ULTIPA_RESPONSE.SearchKhop()
# 		if len(res.data.nodes) > 0:
# 			newData.nodes = res.data.nodes[0].nodes
# 		newData.values = res.data.values
# 		res.data = newData
# 		return res
