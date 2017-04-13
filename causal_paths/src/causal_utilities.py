
from ndex.networkn import NdexGraph
import networkx as nx
from itertools import islice,chain
from networkx import NetworkXNoPath, NetworkXError, NetworkXNotImplemented
from causal_paths import two_way_edges

def get_source_target_network(reference_network, original_edge_map, source_names, target_names, new_network_name, npaths=20, relation_type=None, uuids=None):
    '''
    interpret INDRA statements into causal directed edges
    needs to specify which edges must be doubled to provide both forward and reverse
    :return:
    :rtype:
    '''

    #=====================================================================
    # Filter edges by type.  The following call to indra_causality() will
    # only contain filtered edges and may not add any reverse edges
    #=====================================================================
    if relation_type is not None:
        filter_edges(reference_network, relation_type)

    indra_causality(reference_network, two_way_edges)

    #indra_causality(reference_network, two_way_edgetypes)
    #TODO filter edges based on relation type

    source_ids=get_node_ids_by_names(reference_network, source_names)
    target_ids=get_node_ids_by_names(reference_network, target_names)

    # forward and reverse direction paths for first pair of sources and targets
    forward1 = k_shortest_paths_multi(reference_network, source_names, target_names, npaths)
    reverse1 = k_shortest_paths_multi(reference_network, target_names, source_names, npaths)

    P1 = network_from_paths(reference_network, original_edge_map, forward1, reverse1, source_ids, target_ids, include_reverse=False)  # TODO check efficiency of
    P1.set_name(new_network_name)

    forward1.sort(key = lambda s: len(s))
    reverse1.sort(key = lambda s: len(s))

    return forward1[:npaths], reverse1[:npaths], P1

def k_shortest_paths(G, source, target, k, weight=None):
    try:
        short_path = nx.shortest_simple_paths(G, source, target, weight=weight)
        sliced_short_path = islice(short_path, k)
        #print sliced_short_path
        return list(sliced_short_path)
    except NetworkXNoPath:
        print "no path s: %s, t: %s" % (G.node.get(source)["name"], G.node.get(target)["name"])
        return []
    except NetworkXError:
        print "networkx error"
        return []
    except NetworkXNotImplemented:
        print "networkx not implemented"
        return []

def indra_causality(netn_obj,two_way_edgetypes):
    #==========================================
    # Function for expanding INDRA networks to
    # causal nets. This involves handling edge
    # types where causality could go both ways
    #==========================================
    add_reverse_edges=[]
    for e in netn_obj.edges_iter(data='interaction'):
        if e[2] in two_way_edgetypes:
            add_reverse_edges.append(e)
    for e2 in add_reverse_edges:
        netn_obj.add_edge_between(e2[1],e2[0],interaction=e2[2])

def filter_edges(netn_obj,relation_types):
    for e in netn_obj.edges_iter(data='interaction', keys=True):
        if e[3] not in relation_types:
            netn_obj.remove_edge_by_id(e[2])

def k_shortest_paths_multi(G, source_names, target_names, npaths=20):
    source_ids = get_node_ids_by_names(G,source_names)
    target_ids = get_node_ids_by_names(G,target_names)

    g=nx.DiGraph(G)
    all_shortest_paths = []
    for s in source_ids:
        for t in target_ids:
            try:
                sp_list=k_shortest_paths(g,s,t,npaths)
                for path in sp_list:
                    if len(path) > 1:  # Only include paths that are not self-referencing paths
                        all_shortest_paths.append(path)

            except Exception as inst:
                print "exception in shortest paths: " + str(inst)

    return all_shortest_paths

def network_from_paths(G, original_edge_map, forward, reverse, sources, targets, include_reverse=False):
    M = NdexGraph()
    G.edge = original_edge_map
    edge_tuples=set()
    for path in forward:
        add_path(M, G, path, 'Forward', edge_tuples)
    if include_reverse:
        for path in reverse:
            add_path(M, G, path, 'Reverse', edge_tuples)
    for source in sources:
        source_node = M.node.get(source)
        if(source_node is not None):
            M.node[source]['st_layout'] = 'Source'
    for target in targets:
        target_node = M.node.get(target)
        if(target_node is not None):
            M.node[target]['st_layout'] = 'Target'
    add_edges_from_tuples(M, list(edge_tuples)) # TODO
    return M

def add_path(network, old_network, path, label, edge_tuples, conflict_label='Both'):
    add_path_nodes(network, old_network, path, label, conflict_label)
    for index in range(0, len(path)-1):
        tuple=(path[index],path[index+1]) #TODO add edgeAttr
        edge_tuples.add(tuple)

def add_path_nodes(network, old_network, path, label, conflict_label):
    for node_id in path:
        if node_id not in network.node:
            old_name = old_network.node[node_id]['name']
            network.add_node(node_id, st_layout=label, name=old_name)
        else:
            current_label = network.node[node_id]['st_layout']
            if current_label is not label and current_label is not conflict_label:
                network.node[node_id]['st_layout'] = conflict_label

def add_edges_from_tuples(network, tuples):
    for tuple in tuples:
        network.add_edge_between(tuple[0], tuple[1])
        if(1 in tuple):
            print tuple

def get_node_ids_by_names(G, node_names):
    node_ids = set()
    for name in node_names:
        for id in G.get_node_ids(name, 'name'):
            node_ids.add(id)
    return list(node_ids)

def get_source_target_paths(reference_network, source_names, target_names, npaths=20):
    forward = k_shortest_paths_multi(reference_network, source_names, target_names, npaths)

    forward_paths = node_id_lists_to_paths(forward, reference_network)

    return forward_paths

#====================================
#
# Take a path defined by a list of node ids and create
# a path that alternates between node names and edges
# where the edges are derived from the original network
#
#====================================
def node_id_lists_to_paths(node_id_lists, G):
    paths = []
    for node_id_list in node_id_lists:
        path = node_id_list_to_path(node_id_list, G)
        paths.append(path)
    return paths

def node_id_list_to_path(node_id_list, G):
    node_id_tuples = zip(node_id_list, node_id_list[1:])
    path = []
    first_id = node_id_list[0]
    first_name = G.get_node_name_by_id(first_id)
    path.append(first_name)

    for source_id, target_id in node_id_tuples:
        edge_data = G.get_edge_data(source_id,target_id)
        path.append(edge_data)
        target_name = G.get_node_name_by_id(target_id)
        path.append(target_name)

    return path

def add_path_elements(g, path, node_list, edge_list):
    node_list.extend(path)
    for index in range(0, len(path)-1):
        source_node_id = path[index]
        target_node_id = path[index+1]
        edge_ids =g.get_edge_ids_by_source_target(source_node_id, target_node_id)
        edge_list.extend(edge_ids)
