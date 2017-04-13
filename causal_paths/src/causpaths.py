__author__ = 'aarongary'

import logging
from ndex.networkn import NdexGraph
import ndex.beta.toolbox as toolbox
import causal_utilities as cu
from copy import deepcopy
from path_scoring import PathScoring, EdgeRanking
from causal_paths import preference_schedule_ini

class DirectedPaths:

    def __init__(self):
        logging.info('DirectedPaths: Initializing')

        logging.info('DirectedPaths: Initialization complete')

        self.ref_networks = {}

    def findDirectedPaths(self, network_cx, original_edge_map, source_list, target_list, uuid=None, server=None, npaths=20, relation_type=None):
        self.original_edge_map = deepcopy(network_cx.edge)

        F, R, G_prime = cu.get_source_target_network(network_cx, original_edge_map, source_list, target_list, "Title placeholder", npaths=npaths, relation_type=relation_type)

        complete_forward_list = self.reattach_path_edges(F, network_cx, G_prime)  # TODO check efficiency of this call
        complete_reverse_list = self.reattach_path_edges(R, network_cx, G_prime)  # TODO check efficiency of this call

        subnet = self.reattach_subnet_edges(F, network_cx)

        network_cx = None

        # Apply a cytoscape style from a template network
        template_id = '07762c7e-6193-11e5-8ac5-06603eb7f303'
        toolbox.apply_template(G_prime, template_id)

        return {'forward': F, 'forward_english': complete_forward_list, 'reverse_english': complete_reverse_list, 'reverse': R, 'network': subnet.to_cx()}

    def reattach_subnet_edges(self, F, G):
        important_nodes = [item for sublist in F for item in sublist]

        H = G.subgraph(important_nodes)
        edge_ranking = EdgeRanking(preference_schedule_ini)

        for source in H.edge:
            H[source]

            for target in H[source]:
                best_edge = None
                top_edge = None
                for edge in H[source][target]:
                    H[source][target][edge]["keep"] = False

                    if top_edge is None:
                        top_edge = H[source][target][edge]
                    else:
                        if edge_ranking.edge_type_rank[H[source][target][edge].get("interaction")] < edge_ranking.edge_type_rank[top_edge.get("interaction")]:
                            top_edge = H[source][target][edge]

                top_edge["keep"] = True

        return H

    def reattach_path_edges(self, n_list, G, G_prime):
        result_list = []
        for f in n_list:
            inner = []
            #====================================
            # Take an array of nodes and fill in
            # the edge between the nodes
            #====================================
            for first, second in zip(f, f[1:]):
                if G_prime.edge.get(first) is not None:
                    this_edge = G_prime.edge.get(first).get(second)
                else:
                    this_edge = None

                tmp_edge_list = []

                if(this_edge is not None):
                    if(len(inner) < 1):
                        inner.append(G_prime.node.get(first).get('name'))

                    inner_edge = G.get_edge_data(first,second)

                    for k in inner_edge.keys():
                        tmp_edge_list.append(inner_edge[k])

                    inner.append(tmp_edge_list)
                    inner.append(G_prime.node.get(second).get('name'))

            result_list.append(inner)

        #==========================================
        # Rank the forward paths
        #==========================================
        results_list = []
        try:
            results_list = [f_e_i for f_e_i in result_list if len(result_list) > 0]
        except Exception as e:
            print "error ranking paths"
            print e.message

        path_scoring = PathScoring()

        results_list_sorted = sorted(results_list, lambda x, y: path_scoring.cross_country_scoring(x, y))

        return results_list_sorted