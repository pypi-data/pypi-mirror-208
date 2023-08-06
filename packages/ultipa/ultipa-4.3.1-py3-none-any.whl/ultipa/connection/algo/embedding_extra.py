import sys

from ultipa.connection.algo import ALGO_REQUEST
from ultipa.connection.algo.algo_extra import AlgoExtra
from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST


class EmbeddingExtra(ConnectionBase):

	def __Common__EmbeddingExtra(self, algo_name: str, request: ALGO_REQUEST,
								 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
	   图嵌入算法的接口
		:param algo_name:
		:param request:
		:return:
		'''
		res = AlgoExtra.algoCommonSend(self, algo_name, request, requestConfig)
		return res

	def algo_random_walk(self, request: ALGO_REQUEST.random_walk,
						 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_random_walk(ALGO_REQUEST.Random_Walk(1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_random_walk_node2vec(self, request: ALGO_REQUEST.random_walk_node2vec,
								  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_random_walk_node2vec(ALGO_REQUEST.Random_Walk_Node2vec(1,1,1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_random_walk_struc2vec(self, request: ALGO_REQUEST.random_walk_struc2vec,
								   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_node2vec(ALGO_REQUEST.Node2vec(1,1,1,1,1,1,1,1,1,1,1,1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_node2vec(self, request: ALGO_REQUEST.node2vec,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_node2vec(ALGO_REQUEST.Node2vec(1,1,1,1,1,1,1,1,1,1,1,1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_line(self, request: ALGO_REQUEST.line,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_line(ALGO_REQUEST.Line(edge_property_name='rank',resolution=1,dimension=1,start_alpha=1,neg_num=1,total_sample=1,order=1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_struc2vec(self, request: ALGO_REQUEST.struc2vec,
					   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_line(ALGO_REQUEST.Line(edge_property_name='rank',resolution=1,dimension=1,start_alpha=1,neg_num=1,total_sample=1,order=1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_GraphSAGE(self, request: ALGO_REQUEST.GraphSAGE,
					   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_fastRP(self, request: ALGO_REQUEST.fastRP,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_adamic_adar(self, request: ALGO_REQUEST.adamic_adar,
						 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_bipartite(self, request: ALGO_REQUEST.bipartite,
					   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_variable_compute(self, request: ALGO_REQUEST.variable_compute,
							  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__EmbeddingExtra(sys._getframe().f_code.co_name, request, requestConfig)
