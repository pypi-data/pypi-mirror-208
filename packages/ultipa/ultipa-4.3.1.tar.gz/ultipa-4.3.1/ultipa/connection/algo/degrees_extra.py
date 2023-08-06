import sys

from ultipa.connection.algo import ALGO_REQUEST
from ultipa.connection.algo.algo_extra import AlgoExtra
from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST


class DegreesExtra(ConnectionBase):

	def __Common__DegreesExtra(self, algo_name: str, request: ALGO_REQUEST,
							   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		度相关算法的接口
		:param algo_name:
		:param request:
		:return:
		'''
		res = AlgoExtra.algoCommonSend(self, algo_name, request, requestConfig)
		return res

	def algo_degree(self, request: ALGO_REQUEST.degree,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_out_degree(ALGO_REQUEST.Out_Degree(node_id='12'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__DegreesExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_closeness_centrality(self, request: ALGO_REQUEST.closeness_centrality,
								  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_closeness(ALGO_REQUEST.Closeness(node_id='12'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__DegreesExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_betweenness_centrality(self, request: ALGO_REQUEST.betweenness_centrality,
									requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__DegreesExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_graph_centrality(self, request: ALGO_REQUEST.graph_centrality,
							  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_graph_centrality(ALGO_REQUEST.Graph_Centrality(node_id='12'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__DegreesExtra(sys._getframe().f_code.co_name, request, requestConfig)
