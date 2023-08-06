# from ultipa.connection.connection_base import ConnectionBase
# from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
# from ultipa.utils import UQLMAKER, CommandList
#
#
# class AutoNetExtra(ConnectionBase):
#
# 	def autoNet(self, request: ULTIPA_REQUEST.AutoNet,
# 				requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseAutoNet:
# 		'''
# 		:EXP:conn.autoNet(ULTIPA_REQUEST.AutoNet(srcs='12',dests='21',depth=3,limit=2,select=['name']))
# 		:param request: ULTIPA_REQUEST
# 		:return:
# 		'''
# 		uqlMaker = UQLMAKER(command=CommandList.autoNet, commonParams=requestConfig)
# 		uqlMaker.addParam("srcs", request.srcs)
# 		uqlMaker.addParam("dests", request.dests)
# 		uqlMaker.addParam("depth", request.depth)
# 		uqlMaker.addParam("select", request.select)
# 		uqlMaker.addParam("select_node_properties", request.select_node_properties)
# 		uqlMaker.addParam("select_edge_properties", request.select_edge_properties)
# 		uqlMaker.addParam("limit", request.limit)
# 		uqlMaker.addParam("node_filter", request.node_filter)
# 		uqlMaker.addParam("edge_filter", request.edge_filter)
# 		uqlMaker.addParam("shortest", request.shortest)
# 		uqlMaker.addParam("turbo", request.turbo)
# 		uqlMaker.addParam("no_circle", request.no_circle)
# 		uqlMaker.addParam("boost", request.boost)
# 		res = self.uqlSingle(uqlMaker)
# 		if res.status.code != ULTIPA.Code.SUCCESS:
# 			return res
# 		newData = ULTIPA_RESPONSE.AutoNet()
# 		newData.paths = res.data.paths
# 		res.data = newData
# 		return res
