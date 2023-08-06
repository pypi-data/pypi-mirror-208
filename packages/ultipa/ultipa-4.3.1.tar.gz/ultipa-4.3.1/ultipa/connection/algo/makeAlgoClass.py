algo_sources = [
	{
		"name": 'k_core',
		"param": {
			"name": 'k_core',
			"description": 'the subset of nodes whose neighbours is no less than k in the subset',
			"parameters": {"k": 'size_t,required'},
			"result_opt": '13'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": True,
			"can_write_back": True
		}
	},
	{
		"name": 'node2vec',
		"param": {
			"name": 'node2vec',
			"description": 'node2vec" graph embedding',
			"parameters": {

				"walk_num": 'size_t,required',
				"walk_length": 'size_t,required',
				"window_size": 'size_t,required',
				"p": 'float,required',
				"q": 'float,required',
				"edge_schema_name": 'optional',
				"edge_property_name": 'optional',
				"dimension": 'size_t,required',
				"learning_rate": 'float,required',
				"min_learning_rate": 'float,required',
				"min_frequency": 'size_t,required',
				"sub_sample_alpha": 'float,required',
				"resolution": 'size_t,required',
				"neg_num": 'size_t,required',
				"loop_num": 'size_t,required',
				"buffer_size": '-1 for all paths',
				"limit": '-1 for all nodes in sample paths'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'hyperANF',
		"param": {
			"name": 'hyperANF',
			"description": 'approximate average distance',
			"parameters": {
				"loop_num": 'size_t,required',
				"register_num": 'size_t,required,This value must be in the range[4,30].Default value is 10',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'k_means',
		"param": {
			"name": 'kmeans',
			"description": 'kmeans clustering',
			"parameters": {
				"k": 'size_t,required',
				"start_ids": 'array of nodes,required',
				"node_schema_name": 'node schema,required',
				"node_property_names": 'node attributes,required',
				"distance_type": 'size_t,required,1"Euclidean distance( 欧几里得距离)  2"cosine similarity',
				"loop_num": 'size_t,required'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'graph_centrality',
		"param": {
			"name": 'graph centrality',
			"description": 'graph centrality',
			"parameters": {
				"ids": 'array of nodes,empty for all nodes',
				"limit": '-1 for all results',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'jaccard',
		"param": {
			"name": 'jaccard similarity',
			"description": 'jaccard similarity',
			"parameters": {
				"ids": 'required',
				"ids2": 'optional',
				"limit": '-1 for all result',
				"order": 'optional,ASC or DESC, only valid for pair mode',
				"duplicate": 'optional,1"duplicate, 2(default)"deduplicate'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'GraphSAGE',
		"param": {
			"name": 'GraphSAGE',
			"description": '',
			"parameters": {
				"dimension": 'int,required',
				"normalizationStrength": 'float,optional, 0 as default',
				"iterationWeights": 'float[],optional,[0.0,1.0,1.0] as default',
				"edge_schema_name": 'for weighted random projection,optional',
				"edge_property_name": 'edge attribute, for weighted random projection,optional',
				"propertyDimension": 'int,optional, maximum value is dimension',
				"node_schema_name": 'optional',
				"node_property_names": 'array of node attributes,optional'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'clustering_coefficient',
		"param": {
			"name": 'clustering coefficient',
			"description": 'clustering coefficient of one node',
			"parameters": {
				"ids": 'array of nodes,empty for all nodes',
				"limit": '-1 for all results',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'fastRP',
		"param": {
			"name": 'fastRP',
			"description": 'Fast and Accurate Network Embeddings via Very Sparse Random Projection',
			"parameters": {
				"dimension": 'int,required',
				"normalizationStrength": 'float,optional, 0 as default',
				"iterationWeights": 'float[],optional,[0.0,1.0,1.0] as default',
				"edge_schema_name": 'for weighted random projection,optional',
				"edge_property_name": 'edge attribute, for weighted random projection,optional',
				"propertyDimension": 'int,optional, maximum value is dimension',
				"node_schema_name": 'optional',
				"node_property_names": 'array of node attributes,optional',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'degree',
		"param": {
			"name": 'degree centrality',
			"description": 'degree centrality of one node',
			"parameters": {
				"ids": 'array of nodes,empty for all nodes',
				"edge_schema_name": 'optinal',
				"edge_property_name": 'optinal',
				"limit": '-1 for all results',
				"order": 'optional,ASC or DESC',
				"direction": 'string,optinal, left or right, bi-direction if absent'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'cosine_similarity',
		"param": {
			"name": 'cosine similarity',
			"description": 'cosine similarity',
			"parameters": {
				"ids": 'required',
				"ids2": 'required',
				"node_schema_name": 'required',
				"node_property_names": 'array of node_attributes,required',
				"type": 'optional, 1.(default)normal number, 2.for huge number',
				"limit": 'optional,-1 for all result',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'common_neighbours',
		"param": {
			"name": 'common neighbours',
			"description": 'common neighbours between two nodes',
			"parameters": {
				"ids": 'required',
				"ids2": 'required',
				"type": 'optional, 1.(default)only number, 2.ids',
				"limit": 'optional,-1 for all result',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'triangle_counting',
		"param": {
			"name": 'triangle counting',
			"description": 'triangle counting',
			"parameters": {
				"type": '1"count by edge  2"count by node',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes',
				"limit": '-1 for total_num, otherwise for n triples'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'betweenness_centrality',
		"param": {
			"name": 'betweenness centrality',
			"description": 'betweenness centrality for all nodes',
			"parameters": {
				"ids": 'array of nodes,empty for all nodes',
				"limit": '-1 for all',
				"sample_size": 'optional, -1 for log(total_node_num), -2 for not sampling(most accurate)',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'adamic_adar',
		"param": {
			"name": 'adamic adar',
			"description": 'adamic adar index for each edge',
			"parameters": {},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'bipartite',
		"param": {
			"name": 'bipartite',
			"description": 'bipartite check',
			"parameters": {},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'hanp',
		"param": {
			"name": 'HANP',
			"description": 'Hop Attenuation & Node Preference',
			"parameters": {
				"loop_num": 'size_t,required',
				"node_schema_name": 'required',
				"node_property_name": 'required',
				"edge_schema_name": 'required',
				"edge_property_name": 'required',
				"m": 'float,required',
				"delta": 'float,required',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '6'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'closeness_centrality',
		"param": {
			"name": 'closeness centrality',
			"description": 'closeness centrality',
			"parameters": {
				"ids": 'array of nodes,empty for all nodes',
				"limit": '-1 for all results',
				"direction": 'string,optinal, left or right, bi-direction if absent',
				"sample_size": 'optional, -1 for log(total_node_num), -2 for not sampling(most accurate)',
				"order": 'optional,ASC or DESC'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'connected_component',
		"param": {
			"name": 'connected component',
			"description": 'find all connected components',
			"parameters": {"cc_type": "1 wcc 2scc "},
			"result_opt": '6'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'khop_all',
		"param": {
			"name": 'khop for all nodes',
			"description": 'calculate khop for all nodes',
			"parameters": {
				"depth": 'size_t,required',
				"direction": 'string,optinal, left or right, bi-direction if absent',
				"type": 'size_t,optinal, 1)ids 2)(default)only number'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'variable_compute',
		"param": {
			"name": 'variable_compute',
			"description": 'variable_compute',
			"parameters": {
				"ids": 'nodes',
				"type": 'in(1) / out(1)in(1) - out(1)out(1) - avg(out(1))out(1) / avg(out(1))out(2) - in(2)sum(pow(in(1) - out(1),2) / count())sum(pow(in(1) - out(1),2) / (count() - 1))sqrt(sum(pow(in(1) - out(1),2) / count()))sqrt(sum(pow(in(1) - out(1),2) / (count() - 1)))',
				"limit": '-1 for all nodes'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'knn',
		"param": {
			"name": 'knn',
			"description": 'k-Nearest Neighbors',
			"parameters": {
				"node_id": 'required',
				"node_schema_name": 'required',
				"node_property_names": 'node attrs,required',
				"top_k": 'size_t,required',
				"target_property_name": 'required'
			},
			"result_opt": '4'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": False
		}
	},
	{
		"name": 'line',
		"param": {
			"name": 'LINE',
			"description": 'Large-scale Information Network Embedding',
			"parameters": {
				"edge_schema_name": 'required',
				"edge_property_name": 'required',
				"dimension": 'size_t,required',
				"resolution": 'size_t,required',
				"start_alpha": 'float,required',
				"neg_num": 'size_t,required',
				"total_sample": 'size_t,required',
				"train_order": 'size_t,required,1 or 2'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'louvain',
		"param": {
			"name": 'louvain',
			"description": 'louvain',
			"parameters": {
				"edge_schema_name": 'optinal',
				"edge_property_name": 'optinal,default 1 for each edge if absent',
				"phase1_loop_num": 'size_t,required',
				"min_modularity_increase": 'float,required'
			},
			"result_opt": '15'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": True,
			"can_write_back": True
		}
	},
	{
		"name": 'lpa',
		"param": {
			"name": 'lpa',
			"description": 'label propagation algorithm',
			"parameters": {
				"loop_num": 'size_t,required',
				"node_schema_name": 'optional',
				"node_property_name": 'optional',
				"node_weight_name": 'optional',
				"edge_schema_name": 'optional',
				"edge_weight_name": 'optional',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '6'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'mst',
		"param": {
			"name": 'mst',
			"description": 'minimum spanning tree',
			"parameters": {
				"ids": 'required',
				"edge_schema_name": 'required',
				"edge_property_name": 'required',
				"limit": '-1 for all'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'random_walk_node2vec',
		"param": {
			"name": 'node2vec walk',
			"description": 'node2vec walk to generate the sample data for next-step training',
			"parameters": {
				"walk_length": 'size_t,required',
				"walk_num": 'size_t,required',
				"p": 'float,required',
				"q": 'float,required',
				"edge_schema_name": 'optional',
				"edge_property_name": 'optional',
				"buffer_size": '-1 for all paths'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'page_rank',
		"param": {
			"name": 'Page rank',
			"description": 'Page rank',
			"parameters": {
				"init_value": 'float,optional',
				"loop_num": 'size_t,required',
				"damping": 'float,required',
				"weaken": 'optional,1(default) not weaken, 2 weaken with average number of links going out of all pages (see ArticleRank)',
				"limit": '-1 for all nodes',
				"order": 'ASC or DESC',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '7'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'random_walk',
		"param": {
			"name": 'random walk',
			"description": 'random walk to generate the sample data for next-step training',
			"parameters": {
				"walk_length": 'size_t,required',
				"walk_num": 'size_t,required',
				"edge_schema_name": 'optional',
				"edge_property_name": 'optional,default 1 if absent',
				"ids": 'nodes',
				"limit": '-1 for all nodes'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'struc2vec',
		"param": {
			"name": 'struc2vec',
			"description": 'struc2vec " graph embedding',
			"parameters": {
				"walk_num": 'size_t,required',
				"walk_length": 'size_t,required',
				"k": 'size_t,required',
				"stay_probability": 'float,required',
				"window_size": 'size_t,required',
				"dimension": 'size_t,required',
				"learning_rate": 'float,required',
				"min_learning_rate": 'float,required',
				"min_frequency": 'size_t,required',
				"sub_sample_alpha": 'float,required',
				"resolution": 'size_t,required',
				"neg_num": 'size_t,required',
				"loop_num": 'size_t,required',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'random_walk_struc2vec',
		"param": {
			"name": 'struc2vec walk',
			"description": 'struc2vec walk to generate the sample data for next-step training',
			"parameters": {
				"walk_length": 'size_t,required',
				"walk_num": 'size_t,required',
				"k": 'size_t,required',
				"stay_probability": 'float,required',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	},
	{
		"name": 'subgraph',
		"param": {
			"name": 'subgraph',
			"description": 'subgraph generated by certain nodes',
			"parameters": {"ids": 'array of nodes,required'},
			"result_opt": '13'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": True,
			"can_write_back": True
		}
	},
	{
		"name": 'sybil_rank',
		"param": {
			"name": 'sybil rank',
			"description": 'sybil rank',
			"parameters": {
				"total_trust": 'float,required',
				"trust_seeds": 'array of nodes,required',
				"loop_num": 'size_t,required',
				"sybil_num": 'size_t,required',
				"me": 'optional " 1(default)"few edges between nodes  2"massive edges between nodes'
			},
			"result_opt": '5'
		},
		"result_opt": {
			"can_realtime": True,
			"can_visualization": False,
			"can_write_back": True
		}
	}
]
class_str = f'''
class %s(%s):
    def __init__(self,%s):
        super().__init__(write_back=can_write_back, visualization=can_visualization, realtime=can_realtime)
        %s
'''

for p in algo_sources:
	exdent_class = "AlgoBaseModel"
	class_name = ""
	params_str = ""
	params_name = []
	self_str = ""
	self_name = []
	str = ""
	algo_name = p.get('name')
	params = p.get("param").get("parameters")
	result_opt = p.get("result_opt")
	for k in params.keys():
		if "required" in params[k]:
			if "size_t" in params[k]:

				params_name.append(f"{k}:int")
				self_name.append(f"self.{k}={k}")
			elif "float" in params[k]:
				params_name.append(f"{k}:float")
				self_name.append(f"self.{k}={k}")

			elif "array" in params[k]:
				params_name.append(f"{k}:List")
				self_name.append(f"self.{k}={k}")

			else:
				params_name.append(f"{k}")
				self_name.append(f"self.{k}={k}")

		else:
			if "size_t" in params[k]:
				params_name.append(f"{k}:int=None")
				self_name.append(f"self.{k}={k}")

			elif "float" in params[k]:
				params_name.append(f"{k}:float=None")
				self_name.append(f"self.{k}={k}")

			elif "array" in params[k]:
				params_name.append(f"{k}:List=None")
				self_name.append(f"self.{k}={k}")

			else:
				params_name.append(f"{k}=None")
				self_name.append(f"self.{k}={k}")
	for result_opt_K in result_opt.keys():
		params_name.append(f"{result_opt_K}:bool={result_opt.get(result_opt_K)}")

	class_name = algo_name
	params_str = ','.join(params_name)
	self_str = '\n\t\t'.join(self_name)
	print(class_str % (class_name, exdent_class, params_str, self_str))
