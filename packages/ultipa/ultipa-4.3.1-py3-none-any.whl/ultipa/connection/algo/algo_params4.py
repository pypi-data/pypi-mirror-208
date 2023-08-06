from ultipa.types import ULTIPA
from typing import List


class AlgoBaseModel(ULTIPA.BaseModel):
	def __init__(self, write_back: bool, visualization: bool, force: bool):
		self.write_back = write_back
		self.visualization = visualization
		self.force = force


class k_core(AlgoBaseModel):
	def __init__(self, k: int, force: bool = False, can_visualization: bool = True, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.k = k


class node2vec(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, window_size: int, p: float, q: float, dimension: int,
				 learning_rate: float, min_learning_rate: float,
				 min_frequency: int, sub_sample_alpha: float, resolution: int, neg_num: int, loop_num: int,
				 edge_schema_name=None, edge_property_name=None,
				 buffer_size=None, limit=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.window_size = window_size
		self.p = p
		self.q = q
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.dimension = dimension
		self.learning_rate = learning_rate
		self.min_learning_rate = min_learning_rate
		self.min_frequency = min_frequency
		self.sub_sample_alpha = sub_sample_alpha
		self.resolution = resolution
		self.neg_num = neg_num
		self.loop_num = loop_num
		self.buffer_size = buffer_size
		self.limit = limit


class hyperANF(AlgoBaseModel):
	def __init__(self, loop_num: int, register_num: int, me=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.loop_num = loop_num
		self.register_num = register_num
		self.me = me


class k_means(AlgoBaseModel):
	def __init__(self, k: int, start_ids: List, node_schema_name, node_property_names, distance_type: int,
				 loop_num: int, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.k = k
		self.start_ids = start_ids
		self.node_schema_name = node_schema_name
		self.node_property_names = node_property_names
		self.distance_type = distance_type
		self.loop_num = loop_num


class graph_centrality(AlgoBaseModel):
	def __init__(self, ids: List = None, limit=None, order=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.order = order


class jaccard(AlgoBaseModel):
	def __init__(self, ids, ids2=None, limit=None, order=None, duplicate=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.ids2 = ids2
		self.limit = limit
		self.order = order
		self.duplicate = duplicate


class GraphSAGE(AlgoBaseModel):
	def __init__(self, dimension, normalizationStrength: float = None, iterationWeights: float = None,
				 edge_schema_name=None, edge_property_name=None, propertyDimension=None, node_schema_name=None,
				 node_property_names: List = None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.dimension = dimension
		self.normalizationStrength = normalizationStrength
		self.iterationWeights = iterationWeights
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.propertyDimension = propertyDimension
		self.node_schema_name = node_schema_name
		self.node_property_names = node_property_names


class clustering_coefficient(AlgoBaseModel):
	def __init__(self, ids: List = None, limit=None, order=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.order = order


class fastRP(AlgoBaseModel):
	def __init__(self, dimension, normalizationStrength: float = None, iterationWeights: float = None,
				 edge_schema_name=None, edge_property_name=None, propertyDimension=None, node_schema_name=None,
				 node_property_names: List = None, me=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.dimension = dimension
		self.normalizationStrength = normalizationStrength
		self.iterationWeights = iterationWeights
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.propertyDimension = propertyDimension
		self.node_schema_name = node_schema_name
		self.node_property_names = node_property_names
		self.me = me


class degree(AlgoBaseModel):
	def __init__(self, ids: List = None, edge_schema_name=None, edge_property_name=None, limit=None, order=None,
				 direction=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.limit = limit
		self.order = order
		self.direction = direction


class cosine_similarity(AlgoBaseModel):
	def __init__(self, ids, ids2, node_schema_name, node_property_names: List, type=None, limit=None, order=None,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.ids2 = ids2
		self.node_schema_name = node_schema_name
		self.node_property_names = node_property_names
		self.type = type
		self.limit = limit
		self.order = order


class common_neighbours(AlgoBaseModel):
	def __init__(self, ids, ids2, type=None, limit=None, order=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.ids2 = ids2
		self.type = type
		self.limit = limit
		self.order = order


class triangle_counting(AlgoBaseModel):
	def __init__(self, type=None, me=None, limit=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.type = type
		self.me = me
		self.limit = limit


class betweenness_centrality(AlgoBaseModel):
	def __init__(self, ids: List = None, limit=None, sample_size=None, order=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.sample_size = sample_size
		self.order = order


class adamic_adar(AlgoBaseModel):
	def __init__(self, force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)


class bipartite(AlgoBaseModel):
	def __init__(self, force: bool = False, can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)


class hanp(AlgoBaseModel):
	def __init__(self, loop_num: int, node_schema_name, node_property_name, edge_schema_name, edge_property_name,
				 m: float, delta: float, me=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.loop_num = loop_num
		self.node_schema_name = node_schema_name
		self.node_property_name = node_property_name
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.m = m
		self.delta = delta
		self.me = me


class closeness_centrality(AlgoBaseModel):
	def __init__(self, ids: List = None, limit=None, direction=None, sample_size=None, order=None,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.limit = limit
		self.direction = direction
		self.sample_size = sample_size
		self.order = order


class connected_component(AlgoBaseModel):
	def __init__(self, cc_type=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.cc_type = cc_type


class khop_all(AlgoBaseModel):
	def __init__(self, depth: int, direction=None, type: int = None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.depth = depth
		self.direction = direction
		self.type = type


class variable_compute(AlgoBaseModel):
	def __init__(self, ids=None, type=None, limit=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.type = type
		self.limit = limit


class knn(AlgoBaseModel):
	def __init__(self, node_id, node_schema_name, node_property_names, top_k: int, target_property_name,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = False):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.node_id = node_id
		self.node_schema_name = node_schema_name
		self.node_property_names = node_property_names
		self.top_k = top_k
		self.target_property_name = target_property_name


class line(AlgoBaseModel):
	def __init__(self, edge_schema_name, edge_property_name, dimension: int, resolution: int, start_alpha: float,
				 neg_num: int, total_sample: int, train_order: int, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.dimension = dimension
		self.resolution = resolution
		self.start_alpha = start_alpha
		self.neg_num = neg_num
		self.total_sample = total_sample
		self.train_order = train_order


class louvain(AlgoBaseModel):
	def __init__(self, phase1_loop_num: int, min_modularity_increase: float, edge_schema_name=None,
				 edge_property_name=None, force: bool = False, can_visualization: bool = True,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.phase1_loop_num = phase1_loop_num
		self.min_modularity_increase = min_modularity_increase


class lpa(AlgoBaseModel):
	def __init__(self, loop_num: int, node_schema_name=None, node_property_name=None, node_weight_name=None,
				 edge_schema_name=None, edge_weight_name=None, me=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.loop_num = loop_num
		self.node_schema_name = node_schema_name
		self.node_property_name = node_property_name
		self.node_weight_name = node_weight_name
		self.edge_schema_name = edge_schema_name
		self.edge_weight_name = edge_weight_name
		self.me = me


class mst(AlgoBaseModel):
	def __init__(self, ids, edge_schema_name, edge_property_name, limit=None, force: bool = False,
				 can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.limit = limit


class random_walk_node2vec(AlgoBaseModel):
	def __init__(self, walk_length: int, walk_num: int, p: float, q: float, edge_schema_name=None,
				 edge_property_name=None, buffer_size=None, force: bool = False, can_visualization: bool = False,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.walk_length = walk_length
		self.walk_num = walk_num
		self.p = p
		self.q = q
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.buffer_size = buffer_size


class page_rank(AlgoBaseModel):
	def __init__(self, loop_num: int, damping: float, init_value: float = None, weaken=None, limit=None, order=None,
				 me=None, force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.init_value = init_value
		self.loop_num = loop_num
		self.damping = damping
		self.weaken = weaken
		self.limit = limit
		self.order = order
		self.me = me


class random_walk(AlgoBaseModel):
	def __init__(self, walk_length: int, walk_num: int, edge_schema_name=None, edge_property_name=None, ids=None,
				 limit=None, force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.walk_length = walk_length
		self.walk_num = walk_num
		self.edge_schema_name = edge_schema_name
		self.edge_property_name = edge_property_name
		self.ids = ids
		self.limit = limit


class struc2vec(AlgoBaseModel):
	def __init__(self, walk_num: int, walk_length: int, k: int, stay_probability: float, window_size: int,
				 dimension: int, learning_rate: float, min_learning_rate: float, min_frequency: int,
				 sub_sample_alpha: float, resolution: int, neg_num: int, loop_num: int, me=None,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.walk_num = walk_num
		self.walk_length = walk_length
		self.k = k
		self.stay_probability = stay_probability
		self.window_size = window_size
		self.dimension = dimension
		self.learning_rate = learning_rate
		self.min_learning_rate = min_learning_rate
		self.min_frequency = min_frequency
		self.sub_sample_alpha = sub_sample_alpha
		self.resolution = resolution
		self.neg_num = neg_num
		self.loop_num = loop_num
		self.me = me


class random_walk_struc2vec(AlgoBaseModel):
	def __init__(self, walk_length: int, walk_num: int, k: int, stay_probability: float, me=None,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.walk_length = walk_length
		self.walk_num = walk_num
		self.k = k
		self.stay_probability = stay_probability
		self.me = me


class subgraph(AlgoBaseModel):
	def __init__(self, ids: List, force: bool = False, can_visualization: bool = True,
				 can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.ids = ids


class sybil_rank(AlgoBaseModel):
	def __init__(self, total_trust: float, trust_seeds: List, loop_num: int, sybil_num: int, me=None,
				 force: bool = False, can_visualization: bool = False, can_write_back: bool = True):
		super().__init__(write_back=can_write_back, visualization=can_visualization, force=force)
		self.total_trust = total_trust
		self.trust_seeds = trust_seeds
		self.loop_num = loop_num
		self.sybil_num = sybil_num
		self.me = me
