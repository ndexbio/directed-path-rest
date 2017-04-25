#!/usr/local/bin/python
__author__ = 'aarongary'

import argparse
from bottle import template, Bottle, request, response
import json
import os
import sys
from causal_paths.src.causpaths import DirectedPaths
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import logs
from ndex.networkn import NdexGraph
from copy import deepcopy
from causal_paths.src.path_scoring import EdgeRanking
from causal_paths import preference_schedule_ini
from gain import hash_network

api = Bottle()

log = logs.get_logger('api')

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ref_networks = {}

@api.get('/statuscheck')
def index():
    return "<b>Service is up and running</b>!"

@api.get('/ontologysub/<uuid>/query/<nodeId>')
def get_ontology_sub_id(uuid, nodeId):
    sub_id = hash_network.get_ontology_sub_network(uuid, nodeId)

    return dict(data=sub_id)

@api.post('/directedpath/query')
def find_directed_path_directed_post():
    uuid = None
    server = None
    network = None
    original_edge_map = None
    data = request.files.get('network_cx')
    query_string = dict(request.query)

    #============================
    # VERIFY FILE CAN BE PARSED
    # OR UUID WAS SUPPLIED
    #============================
    if('uuid' in query_string.keys() and len(query_string['uuid']) > 0):
        if('server' in query_string.keys() and len(query_string['server']) > 0):
            server = query_string['server']
            if("http" not in server):
                server = "http://" + query_string['server']

            uuid = query_string['uuid']

            network, original_edge_map = get_reference_network(uuid, server)
            uuid = None
        else:
            response.status = 400
            response.content_type = 'application/json'
            return json.dumps({'message': 'Server must be supplied if UUID is used'})
    else:
        if data and data.file:
            try:
                read_file = data.file.read()
                network = NdexGraph(cx=json.loads(read_file))
                original_edge_map = deepcopy(network.edge)
            except Exception as e:
                response.status = 400
                response.content_type = 'application/json'
                return json.dumps({'message': 'Network file is not valid CX/JSON. Error --> ' + e.message})
        else:
            response.status = 400
            response.content_type = 'application/json'
            return json.dumps({'message': 'Valid CX/JSON file not found and uuid not supplied.'})

    #==================================
    # VERIFY SOURCE NODES ARE PRESENT
    #==================================
    if('source' in query_string.keys() and len(query_string['source']) > 0):
        source = query_string['source'].split(",")
    else:
        response.status = 400
        response.content_type = 'application/json'
        return json.dumps({'message': 'Missing source list in query string. Example: /query?source=EGFR&target=MAP2K1 MAP2K2&pathnum=5'})
        #raise KeyError("missing source list")

    #==================================
    # VERIFY TARGET NODES ARE PRESENT
    #==================================
    if('target' in query_string.keys() and len(query_string['target']) > 0):
        target = query_string['target'].split(",")
    else:
        response.status = 400
        response.content_type = 'application/json'
        return json.dumps({'message': 'Missing target list in query string. Example: /query?source=EGFR&target=MAP2K1 MAP2K2&pathnum=5'})
        #raise KeyError("missing target list")

    #=================
    # PARSE N TO INT
    #=================
    pathnum = query_string.get('pathnum')
    if(pathnum is not None):
        if pathnum.isdigit():
            pathnum = int(pathnum, 10)
        else:
            pathnum = 20
    else:
            pathnum = 20

    directedPaths = DirectedPaths()

    return_paths = None

    if('relationtypes' in query_string.keys() and len(query_string['relationtypes']) > 0):
        relation_types = query_string['relationtypes'].split()
        return_paths = directedPaths.findDirectedPaths(network, original_edge_map, source, target, npaths=pathnum, relation_type=relation_types)
    else:
        return_paths = directedPaths.findDirectedPaths(network, original_edge_map, source, target, npaths=pathnum)
    directedPaths = None
    result = dict(data=return_paths)
    return result

@api.get('/getPreferenceSchedule')
def get_preference_schedule():
    edgeRanking = EdgeRanking(preference_schedule_ini)
    return_dict = edgeRanking.get_nice_preference_schedule()

    return dict(data=return_dict)

def get_reference_network(uuid, host):
    if ref_networks.get(uuid) is None:
        G = NdexGraph(server=host, uuid=uuid)

        ref_networks[uuid] = G
    else:
        print "INFO: using cached network."

    return deepcopy(ref_networks.get(uuid)), ref_networks.get(uuid).edge

# run the web server
def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=5603)
    args = parser.parse_args()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'
    try:
        server = WSGIServer(('0.0.0.0', args.port), api, handler_class=WebSocketHandler)
        log.info('entering main loop')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('exiting main loop')
    except Exception as e:
        str = 'could not start web server: %s' % e
        log.error(str)
        print str
        status = 1

    log.info('exiting with status %d', status)
    return status

if __name__ == '__main__':
    sys.exit(main())