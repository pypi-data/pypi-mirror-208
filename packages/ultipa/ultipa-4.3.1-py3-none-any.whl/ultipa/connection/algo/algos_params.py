from ultipa.types import ULTIPA
from typing import List

'''定义算法参数的类'''


class AlgoBaseModel(ULTIPA.BaseModel):
	def __init__(self, write_back: bool, visualization: bool, force):
		self.write_back = write_back
		self.visualization = visualization
		self.force = force


class Out_Degree(AlgoBaseModel):
	def __init__(self, node_id: int, edge_property_name: str = None, write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id = node_id
		self.edge_property_name = edge_property_name


class In_Degree(Out_Degree):
	pass


class Degree(Out_Degree):
	pass


class Out_Degree_All(AlgoBaseModel):
	def __init__(self, ids: List[str], limit: int = -1, order: str = 'ASC', write_back: bool = False,
				 edge_property_name: str = None, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.order = order
		self.write_back = write_back
		self.edge_property_name = edge_property_name


class In_Degree_All(Out_Degree_All):
	pass


class Degree_All(Out_Degree_All):
	pass


class Closeness(AlgoBaseModel):
	def __init__(self, ids: List, limit: int = -1, write_back: bool = False, visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.ids = ids
		self.write_back = write_back
		self.limit = limit


class Out_Closeness(Closeness):
	pass


class In_Closeness(Closeness):
	pass


class Graph_Centrality(AlgoBaseModel):

	def __init__(self, node_id: str, write_back: bool = False, visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id = node_id


# class Graph_Centrality_All(Closeness):
#     pass


class Betweenness_Centrality(AlgoBaseModel):
	def __init__(self, limit: int = -1, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.write_back = write_back
		self.limit = limit


class Khop_all(AlgoBaseModel):
	def __init__(self, depth: int, type: int = 2, direction: str = None, me: str = None, write_back: bool = False,
				 visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.depth = depth
		self.direction = direction
		self.me = me
		self.type = type if type == 1 else 2
		self.write_back = write_back


class Knn(AlgoBaseModel):
	def __init__(self, node_id: int, node_property_names: List[str], target_property_name: str, top_k: int,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id = node_id
		self.node_property_names = node_property_names
		self.target_property_name = target_property_name
		self.top_k = top_k


class Kcore(AlgoBaseModel):
	def __init__(self, k: int, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.k = k
		self.write_back = write_back


class Mst(AlgoBaseModel):
	def __init__(self, ids: List, edge_property_name: str, limit: int = -1, write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.edge_property_name = edge_property_name
		self.write_back = write_back


class Page_Rank(AlgoBaseModel):
	def __init__(self, loop_num: int, damping: float, init_value: float = None, order: str = 'ASC',
				 write_back: bool = False, limit: int = -1,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.loop_num = loop_num
		self.damping = damping
		self.limit = limit
		self.init_value = init_value
		self.order = order
		self.write_back = write_back


class Sybil_Rank(AlgoBaseModel):
	def __init__(self, loop_num: int, sybil_num: int, trust_seeds: List[int], total_trust: int,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.trust_seeds = trust_seeds
		self.total_trust = total_trust
		self.loop_num = loop_num
		self.sybil_num = sybil_num
		self.write_back = write_back


class Jaccard(AlgoBaseModel):
	def __init__(self, ids1: List[int], ids2: List[int] = None, limit: int = -1, order: str = 'ASC',
				 write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.ids1 = ids1
		self.ids2 = ids2
		self.limit = limit
		self.order = order
		self.write_back = write_back


class Cosine_Similarity(AlgoBaseModel):
	def __init__(self, node_id1: int, node_id2: int, node_property_names: List[str], write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id1 = node_id1
		self.node_id2 = node_id2
		self.node_property_names = node_property_names
		self.write_back = write_back


class Connected_Component(AlgoBaseModel):
	def __init__(self, cc_type: int, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.write_back = write_back
		self.cc_type = cc_type


class Lpa(AlgoBaseModel):
	def __init__(self, loop_num: int, node_property_name: str = None, node_weight_name: str = None,
				 edge_weight_name: str = None, write_back: bool = False, visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.loop_num = loop_num
		self.node_property_name = node_property_name
		self.node_weight_name = node_weight_name
		self.edge_weight_name = edge_weight_name
		self.write_back = write_back


class Hanp(AlgoBaseModel):
	def __init__(self, loop_num: int, edge_property_name: str, node_property_name: str, m: float, delta: float,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.loop_num = loop_num
		self.edge_property_name = edge_property_name
		self.node_property_name = node_property_name
		self.m = m
		self.delta = delta
		self.write_back = write_back


class K_Means(AlgoBaseModel):
	def __init__(self, start_ids: List[int], k: int, node_property_names: List[str], distance_type: int,
				 loop_num: int, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.k = k
		self.start_ids = start_ids
		self.node_property_names = node_property_names
		self.distance_type = distance_type if distance_type == 2 else 1
		self.loop_num = loop_num
		self.write_back = write_back


class Louvain(AlgoBaseModel):
	def __init__(self, phase1_loop_num: int, min_modularity_increase: float,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.phase1_loop_num = phase1_loop_num
		self.min_modularity_increase = min_modularity_increase
		self.write_back = write_back


class Triangle_Counting(AlgoBaseModel):
	def __init__(self, type: int = 1, limit: int = -1, write_back: bool = False, visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.write_back = write_back
		self.type = type
		self.limit = limit


class HyperANF(AlgoBaseModel):
	def __init__(self, loop_num: int, register_num: int, write_back: bool = False, visualization: bool = False,
				 force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.loop_num = loop_num
		self.register_num = register_num
		self.write_back = write_back


class Common_neighbours(AlgoBaseModel):
	def __init__(self, node_id1: int, node_id2: int, write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id1 = node_id1
		self.node_id2 = node_id2
		self.write_back = write_back


class Subgraph(AlgoBaseModel):
	def __init__(self, node_ids: List[int], write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_ids = node_ids
		self.write_back = write_back


class Clustering_Coefficient(AlgoBaseModel):
	def __init__(self, node_id: str, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.node_id = node_id
		self.write_back = write_back


class Clustering_Coefficient_all(AlgoBaseModel):
	def __init__(self, ids: str = None, limit: int = -1, order: str = 'ASC', write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.ids = ids
		self.write_back = write_back
		self.limit = limit
		self.order = order


class Random_Walk(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, edge_property_name: str = None, write_back: bool = False,
				 visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.edge_property_name = edge_property_name
		self.write_back = write_back


class Random_Walk_Node2vec(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, p: float, q: float = None, edge_property_name: str = None,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.p = p
		self.q = q
		self.edge_property_name = edge_property_name
		self.write_back = write_back


class Random_Walk_Stuc2vec(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, k: float, stay_probability: float = None,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.k = k
		self.stay_probability = stay_probability
		self.write_back = write_back


class Node2vec(AlgoBaseModel):
	def __init__(self, buffer_size: int, walk_num: int, loop_num: int, walk_length: int, p: float, q: float,
				 window_size: int,
				 dimension: int, learning_rate: float, min_learning_rate: float, resolution: int,
				 iter_num: int, sub_sample_alpha: float = None, neg_num: int = None, min_frequency: int = None,
				 edge_property_name: str = None, write_back: bool = False, visualization: bool = False,
				 force: bool = False, limit: int = -1):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.walk_num = walk_num
		self.buffer_size = buffer_size
		self.loop_num = loop_num
		self.walk_length = walk_length
		self.p = p
		self.q = q
		self.window_size = window_size
		self.dimension = dimension
		self.learning_rate = learning_rate
		self.min_learning_rate = min_learning_rate
		self.sub_sample_alpha = sub_sample_alpha
		self.resolution = resolution
		self.neg_num = neg_num
		self.iter_num = iter_num
		self.min_frequency = min_frequency
		self.edge_property_name = edge_property_name
		self.write_back = write_back
		self.limit = limit


class Line(AlgoBaseModel):
	def __init__(self, edge_property_name: str, resolution: int, dimension: int, start_alpha: float, neg_num: int,
				 total_sample: int,
				 train_order: int, write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.edge_property_name = edge_property_name
		self.resolution = resolution
		self.dimension = dimension
		self.start_alpha = start_alpha
		self.neg_num = neg_num
		self.total_sample = total_sample
		self.train_order = 1 if train_order == 1 else 2
		self.write_back = write_back


class Struc2vec(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, k: int, stay_probability: float, window_size: float,

				 dimension: int, learning_rate: float, min_learning_rate: float, resolution: int,
				 loop_num: int, sub_sample_alpha: float = None, neg_num: int = None, min_frequency: int = None,
				 write_back: bool = False, visualization: bool = False, force: bool = False):
		super().__init__(write_back=write_back, visualization=visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.k = k
		self.stay_probability = stay_probability
		self.window_size = window_size
		self.min_learning_rate = min_learning_rate
		self.dimension = dimension
		self.learning_rate = learning_rate
		self.sub_sample_alpha = sub_sample_alpha
		self.resolution = resolution
		self.neg_num = neg_num
		self.loop_num = loop_num
		self.min_frequency = min_frequency
		self.write_back = write_back


class Dv(ULTIPA.BaseModel):
	def __init__(self, algo_name: str, id: int, top: int = 5, total: int = 100):
		self.algo_name = algo_name
		self.id = id
		self.top = top
		self.total = total
