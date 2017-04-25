__author__ = 'aarongary'
from ndex.networkn import NdexGraph
from ndex.client import Ndex
import pymongo

mongodb_uri = 'mongodb://localhost'

def get_ontology_sub_network(uuid, sub_id):
    client = pymongo.MongoClient()
    db = client.ndex

    node_lookup_collection = db.node_lookup

    ndex_collection_found = node_lookup_collection.find_one({'uuid': uuid})

    if ndex_collection_found is None:
        index_ontology_graph(uuid)

    ndex_collection_found = node_lookup_collection.find_one({'uuid': uuid})

    if ndex_collection_found is not None:
        if ndex_collection_found.get('nodes') is not None:
            return_sub_id = ndex_collection_found.get('nodes').get(sub_id)
            client.close()

            return return_sub_id
    else:
        client.close()

        print 'couldn\'t find ontology'
        return None

def index_ontology_graph(uuid):
    client = pymongo.MongoClient()
    db = client.ndex

    node_lookup_collection = db.node_lookup

    ndex_collection_found = node_lookup_collection.find_one({'uuid': uuid})

    if ndex_collection_found is None:
        ndex = Ndex("http://public.ndexbio.org", "scratch", "scratch")

        response = ndex.get_network_as_cx_stream(uuid)

        fanGo_cx = response.json()

        G = NdexGraph(cx=fanGo_cx)

        nodes_values = {}

        for node_id, data in G.nodes_iter(data=True):
            if data.get('name') is not None and data.get('ndex:internalLink') is not None:
                nodes_values[data.get('name')] = data.get('ndex:internalLink')
                #print data.get('name') + ' : ' + data.get('ndex:internalLink')

        node_lookup_collection.save({'uuid': uuid, 'nodes': nodes_values})
        node_lookup_collection.ensure_index([("uuid" , pymongo.ASCENDING)])
        #print json.dumps(fanGo_cx)

    client.close()

if __name__ == "__main__":
    # return_uuid = get_ontology_sub_network('f6aa4772-297b-11e7-8f50-0ac135e8bacf', 'CLIXO:119')
    print "ready"



