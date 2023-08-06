# from ultipa.connection.connection_base import ConnectionBase
# from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
# from ultipa.utils import UQLMAKER, CommandList
#
#
# class SearchABExtra(ConnectionBase):
#
# 	def searchAB(self, request: ULTIPA_REQUEST.SearchAB,
# 				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.SearchAB:
# 		'''
# 		:EXP: conn.searchAB(ULTIPA_REQUEST.SearchAB(src='12',dest='21',depth=3,limit=5,select=['*'))
# 		:param req: ULTIPA_REQUEST
# 		:return:
# 		'''
# 		uqlMaker = UQLMAKER(command=CommandList.ab, commonParams=requestConfig)
# 		request.osrc and uqlMaker.addParam("osrc", request.osrc) or uqlMaker.addParam("src", request.src)
# 		request.odest and uqlMaker.addParam("odest", request.odest) or uqlMaker.addParam("dest", request.dest)
# 		uqlMaker.addParam("depth", request.depth)
# 		uqlMaker.addParam("limit", request.limit)
# 		uqlMaker.addParam("node_filter", request.node_filter)
# 		uqlMaker.addParam("edge_filter", request.edge_filter)
# 		uqlMaker.addParam("select", request.select)
# 		uqlMaker.addParam("select_node_properties", request.select_node_properties)
# 		uqlMaker.addParam("select_edge_properties", request.select_edge_properties)
# 		uqlMaker.addParam("shortest", request.shortest)
# 		uqlMaker.addParam("path_ascend", request.path_ascend)
# 		uqlMaker.addParam("path_descend", request.path_descend)
# 		uqlMaker.addParam("direction", request.direction)
# 		uqlMaker.addParam("turbo", request.turbo)
# 		uqlMaker.addParam("no_circle", request.no_circle)
# 		uqlMaker.addParam("boost", request.boost)
# 		res = self.uqlSingle(uqlMaker)
# 		if res.status.code != ULTIPA.Code.SUCCESS:
# 			return res
# 		newData = ULTIPA_RESPONSE.SearchPath()
# 		newData.paths = res.data.paths
# 		res.data = newData
# 		return res
