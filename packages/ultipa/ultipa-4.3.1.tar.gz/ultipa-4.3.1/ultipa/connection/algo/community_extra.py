import sys

from ultipa.connection.algo import ALGO_REQUEST
from ultipa.connection.algo.algo_extra import AlgoExtra
from ultipa.connection.connection_base import ConnectionBase
from ultipa.types import ULTIPA_REQUEST


class CommunityExtra(ConnectionBase):

	def __Common__CommunityExtra(self, algo_name: str, request: ALGO_REQUEST,
								 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		社区算法的接口
		:param algo_name:
		:param request:
		:return:
		'''
		res = AlgoExtra.algoCommonSend(self, algo_name, request, requestConfig)
		return res

	def algo_khop_all(self, request: ALGO_REQUEST.khop_all,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_k_hop(ALGO_REQUEST.Khop(2))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_knn(self, request: ALGO_REQUEST.knn,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_k_hop(ALGO_REQUEST.Khop(2))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_k_core(self, request: ALGO_REQUEST.k_core,
					requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_k_hop(ALGO_REQUEST.Khop(2))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_mst(self, request: ALGO_REQUEST.mst,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_mst(ALGO_REQUEST.Mst('12','rank'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_page_rank(self, request: ALGO_REQUEST.page_rank,
					   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_page_rank(ALGO_REQUEST.Page_Rank(1,1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_sybil_rank(self, request: ALGO_REQUEST.sybil_rank,
						requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_sybil_rank(ALGO_REQUEST.Sybil_Rank([1,2,3,4,5,6],1,1,1))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_jaccard(self, request: ALGO_REQUEST.jaccard,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_jaccard(ALGO_REQUEST.Jaccard('12','21'))
		:EXP: conn.algo_jaccard(ALGO_REQUEST.Jaccard('12',top=5))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_cosine_similarity(self, request: ALGO_REQUEST.cosine_similarity,
							   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_cosine_similarity(ALGO_REQUEST.Cosine_Similarity(12,21,['age']))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_connected_component(self, request: ALGO_REQUEST.connected_component,
								 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_connected_component(ALGO_REQUEST.Connected_Component())
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_lpa(self, request: ALGO_REQUEST.lpa,
				 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_lpa(ALGO_REQUEST.Lpa(2,'name'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_hanp(self, request: ALGO_REQUEST.hanp,
				  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_lpa(ALGO_REQUEST.Lpa(2,'name'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_k_means(self, request: ALGO_REQUEST.k_means,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_lpa(ALGO_REQUEST.Lpa(2,'name'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_louvain(self, request: ALGO_REQUEST.louvain,
					 requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_louvain(ALGO_REQUEST.Louvain(1,1,'name'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_triangle_counting(self, request: ALGO_REQUEST.triangle_counting,
							   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		conn.algo_triangle_counting(ALGO_REQUEST.Triangle_Counting())
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_hyperANF(self, request: ALGO_REQUEST.hyperANF,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_common_neighbours(self, request: ALGO_REQUEST.common_neighbours,
							   requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, requestConfig)

	def algo_subgraph(self, request: ALGO_REQUEST.subgraph,
					  requestConfig: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, commonReq)

	def algo_clustering_coefficient(self, request: ALGO_REQUEST.clustering_coefficient,
									commonReq: ULTIPA_REQUEST.RequestConfig = ULTIPA_REQUEST.RequestConfig()):
		'''
		:EXP: conn.algo_clustering_coefficient(ALGO_REQUEST.Clustering_Coefficient('12'))
		:param request: ALGO_REQUEST
		:return:
		'''
		return self.__Common__CommunityExtra(sys._getframe().f_code.co_name, request, commonReq)
