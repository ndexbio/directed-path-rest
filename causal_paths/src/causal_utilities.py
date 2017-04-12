
from ndex.networkn import NdexGraph
import networkx as nx
from itertools import islice,chain
from networkx import NetworkXNoPath, NetworkXError, NetworkXNotImplemented
from causal_paths import two_way_edges

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

def shortest_paths_csv(sp_list, netn_obj, fh, path_counter=0):
    for l in sp_list:
        path_counter=path_counter+1
        genes_in_path=netn_obj.get_node_names_by_id_list(l)
        for i in xrange(0,len(genes_in_path)-1):
            es=netn_obj.get_edge_ids_by_node_attribute(genes_in_path[i],genes_in_path[i+1])
            for ed in es:
                fh.write(str(genes_in_path[i])+'\t'
                         + str(netn_obj.get_edge_attribute_by_id(ed,'interaction'))
                         +'\t'+str(genes_in_path[i+1])+'\t'+str(path_counter)+'\n')
    return path_counter

def source_list_to_target_list_all_shortest(sources,targets,netn_obj,npaths=20,fh=open('out_file.txt','w')):
    names = [netn_obj.node[n]['name'] for n in netn_obj.nodes_iter()]
    sources_list=[netn_obj.get_node_ids(i) for i in list(set(sources).intersection(set(names)))]
    sources_ids= list(chain(*sources_list))
    targets_list=[netn_obj.get_node_ids(i) for i in list(set(targets).intersection(set(names)))]
    targets_ids= list(chain(*targets_list))
    path_counter=0
    g=nx.DiGraph(netn_obj)
    for s in sources_ids:
        for t in targets_ids:
            sp_list=k_shortest_paths(g,s,t,npaths)
            path_counter=shortest_paths_csv(sp_list, netn_obj, fh, path_counter=path_counter)


def sources_to_targets_dict(sources,targets,netn_obj,npaths=1):
    names = [netn_obj.node[n]['name'] for n in netn_obj.nodes_iter()]
    sources_list=[netn_obj.get_node_ids(i) for i in list(set(sources).intersection(set(names)))]
    sources_ids= list(chain(*sources_list))
    targets_list=[netn_obj.get_node_ids(i) for i in list(set(targets).intersection(set(names)))]
    targets_ids= list(chain(*targets_list))
    g=nx.DiGraph(netn_obj)
    path_dict={}
    path_counter=0
    for s in sources_ids:
        for t in targets_ids:
            sp_list=k_shortest_paths(g,s,t,npaths)
            for sp in sp_list:
                path_dict[path_counter]=sp
                path_counter=path_counter+1
    return path_dict
#
# def add_edge_property_from_dict(netn_obj,dictionary):
#     """Takes a dictionary with keys of properties which are to be added to a list of edges"""
#     for k in dictionary.keys():
#         for e in dictionary[k]:
#             netn_obj.set_edge_attribute(e,str(k),value)

def indra_causality(netn_obj,two_way_edgetypes):
    #Function for expanding INDRA networks to causal nets.  This involves handling edge types where causality could go both ways
    add_reverse_edges=[]
    for e1 in netn_obj.edges_iter():
        mystr = e1
    for e in netn_obj.edges_iter(data='interaction'):
        if e[2] in two_way_edgetypes:
            add_reverse_edges.append(e)
    for e2 in add_reverse_edges:
        netn_obj.add_edge_between(e2[1],e2[0],interaction=e2[2])

def filter_edges(netn_obj,relation_types):
    for e in netn_obj.edges_iter(data='interaction', keys=True):
        if e[3] not in relation_types:
            netn_obj.remove_edge_by_id(e[2])
            #print "removing edge %s" % e[3] #.add_edge_between(e2[1],e2[0],interaction=e2[2])

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

# get_source_target_paths(G, ['MAP2K1'], ['MMP9'], npaths=20)
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
        #edge_ids = G.get_edge_ids_by_source_target(source_id, target_id)

    return path

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

def get_source_target_network_batch(reference_network, source_target_names, new_network_name, npaths=20, relation_type=None, uuids=None):

    # interpret INDRA statements into causal directed edges
    # needs to specify which edges must be doubled to provide both forward and reverse

    #=====================================================================
    # Filter edges by type.  The following call to indra_causality() will
    # only contain filtered edges and may not add any reverse edges
    #=====================================================================
    if relation_type is not None:
        filter_edges(reference_network, relation_type)

    #print two_way_edges

    indra_causality(reference_network, two_way_edges)
    #TODO filter edges based on relation type

    return_matrix = []

    g=nx.DiGraph(reference_network)
    for st in source_target_names:
        s = st.get("sources")
        targets = st.get("targets")

        for t in targets:
            print "processing %s %s" % (s, t)
            source_ids=get_node_ids_by_names(reference_network, s)
            target_ids=get_node_ids_by_names(reference_network, t)

            forward1 = []
            for s_id in source_ids:
                for t_id in target_ids:
                    try:
                        sp_list=k_shortest_paths(g,s_id,t_id,npaths)
                        for path in sp_list:
                            forward1.append(path)
                    except Exception as inst:
                        print "exception in shortest paths: " + str(inst)

            reverse1 = []  # k_shortest_paths_multi(reference_network, s, t, npaths)

            P1 = network_from_paths(reference_network, forward1, reverse1, source_ids, target_ids, include_reverse=False)  # TODO check efficiency of
            P1.set_name(new_network_name)
            forward1.sort(key = lambda s: len(s))

            forward_english = label_node_list(forward1, reference_network, P1)

            return_matrix.append({'forward': forward1[:npaths], 'reverse': reverse1[:npaths], "forward_english": forward_english})

    return return_matrix

def label_node_list(n_list, G, G_prime):
    outer = []
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

        outer.append(inner)

    return outer

def get_source_target_network_new (network, source_names, target_names, new_network_name, npaths=20, direction='all'):
    # forward and reverse direction paths for first pair of sources and targets
    forward = []
    reverse = []
    if direction == 'all' or direction == 'forward':
        forward = k_shortest_paths_multi(network, source_names, target_names, npaths)
    if direction == 'all' or direction == 'reverse':
        reverse = k_shortest_paths_multi(network, target_names, source_names, npaths)
        
    forward_node_id_list, forward_edge_id_list = path_element_lists(network, forward)
    forward_node_id_set = set(forward_node_id_list)
    reverse_node_id_list, reverse_edge_id_list = path_element_lists(network, reverse)
    reverse_node_id_set = set(reverse_node_id_list)
    node_id_set = forward_node_id_set.union(reverse_node_id_set)
    edge_id_set = set(forward_edge_id_list).union(set(reverse_edge_id_list))

    for node_id in forward_node_id_list:
        network.set_node_attribute(node_id, "st_layout", "Forward")
    for node_id in reverse_node_id_list:
            network.set_node_attribute(node_id, "st_layout", "Reverse")
    overlap_node_id_list = list(set(forward_node_id_list).intersection(set(reverse_node_id_list)))
    for node_id in overlap_node_id_list:
        network.set_node_attribute(node_id, "st_layout", "Both")

    print "computed node and edge sets"

    source_ids=get_node_ids_by_names(network, source_names)
    for node_id in source_ids:
        network.set_node_attribute(node_id, "st_layout", "Target")
    target_ids=get_node_ids_by_names(network, target_names)
    for node_id in target_ids:
        network.set_node_attribute(node_id, "st_layout", "Source")

    reduce_network_by_ids(network, node_id_set, edge_id_set)

    network.set_name(new_network_name)
    print "path network ready "

    forward.sort(key = lambda s: len(s))
    reverse.sort(key = lambda s: len(s))
    return {'forward': forward[:npaths], 'reverse': reverse[:npaths], 'network': network}


# destructively modifies g
def reduce_network_by_ids(g, node_id_set, edge_id_set):

    g_node_id_set = set(g.nodes())
    g_edge_id_list = []
    for edge in g.edges(keys=True):
        g_edge_id_list.append(edge[2])

    g_edge_id_set = set(g_edge_id_list)

    node_ids_to_remove = list(g_node_id_set.difference(node_id_set))
    edge_ids_to_remove = list(g_edge_id_set.difference(edge_id_set))

    for edge_id in edge_ids_to_remove:
        g.remove_edge_by_id(edge_id)

    for node_id in node_ids_to_remove:
        g.remove_node(node_id)

    print "removal done"

def path_element_lists(g, paths):
    node_list = []
    edge_list = []
    for path in paths:
        add_path_elements(g, path, node_list, edge_list)
    return list(set(node_list)), list(set(edge_list))

def add_path_elements(g, path, node_list, edge_list):
    node_list.extend(path)
    for index in range(0, len(path)-1):
        source_node_id = path[index]
        target_node_id = path[index+1]
        edge_ids =g.get_edge_ids_by_source_target(source_node_id, target_node_id)
        edge_list.extend(edge_ids)
