# from ultipa.connection.connection_base import ConnectionBase
# from ultipa.types import ULTIPA_REQUEST, ULTIPA, ULTIPA_RESPONSE
# from ultipa.utils import UQLMAKER, CommandList
# from ultipa.utils.errors import ParameterException
#
#
# class NodeSpreadExtra(ConnectionBase):
# 	def nodeSpread(self, request: ULTIPA_REQUEST.NodeSpread,
# 				   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()) -> ULTIPA_RESPONSE.ResponseNodeSpread:
# 		'''
# 		:EXP: conn.nodeSpread(ULTIPA_REQUEST.NodeSpread(src='12',depth=1,limit=10))
# 		:param req: ULTIPA_REQUEST
# 		:return:
# 		'''
# 		uqlMaker = UQLMAKER(command=CommandList.nodeSpread, commonParams=requestConfig)
# 		if request.src != None:
# 			uqlMaker.addParam("src", request.src)
# 		elif request.osrc != None:
# 			uqlMaker.addParam("osrc", request.osrc)
# 		else:
# 			raise ParameterException('src or osrc is required')
# 		uqlMaker.addParam("depth", request.depth, required=False)
# 		uqlMaker.addParam("limit", request.limit)
# 		uqlMaker.addParam("select", request.select)
# 		uqlMaker.addParam("select_node_properties", request.select_node_properties)
# 		uqlMaker.addParam("select_edge_properties", request.select_edge_properties)
# 		uqlMaker.addParam("node_filter", request.node_filter)
# 		uqlMaker.addParam("edge_filter", request.edge_filter)
# 		uqlMaker.addParam("spread_type", request.spread_type)
# 		uqlMaker.addParam("direction", request.direction)
# 		res = self.uqlSingle(uqlMaker)
# 		if res.status.code != ULTIPA.Code.SUCCESS:
# 			return res
# 		uqlReply = res.data
# 		newData = ULTIPA_RESPONSE.NodeSpread()
# 		if len(uqlReply.paths) > 0:
# 			newData.paths = res.data.paths
# 		else:
# 			newData.paths = []
# 		res.data = newData
# 		return res
