directed-path-rest
===========

REST service for finding directed paths in a reference network.

## REST API

**Directed path search**
----
  Returns a set of forward paths in [NodeId, NodeId, NodeId] format as well as [NodeLabel,EdgesInBetween,NextNodeLabel] format.  Also returns a subnetwork comprised of the found paths.

* **URL**

  /directedpath/query

* **Method:**

  `POST`
  
*  **URL Params**

   **Required:**
 
   `uuid=[NDEx network identifier]`
   
   `server=[NDEx server host name]`
   
   `source=[comma delimited string of source nodes]`
   
   `target=[comma delimited string of target nodes]`
   
   
   **Optional:**
   
   `pathnum=[integer number of paths to return.  Default is 20]`
 
* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{"data": {"forward": [[19,65,193],[39, 47, 66]],...}}`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{ message : "Missing source list in query string." }`


* **Example:**

  * **POST URL:** `http://general.bigmech.ndexbio.org:5603/directedpath/query?source=MAP2K5,KRAS,MYC,BRAF&target=MAPK7,ERK&pathnum=15&uuid=76ce8073-002a-11e6-b550-06603eb7f303&server=public.ndexbio.org`



**Get preference schedule**
----
  Returns the current preference schedule of edge types

* **URL**
    /getPreferenceSchedule

* **Method:**
    `GET`
  
*  **URL Params**
    None
   
* **Data Params**
    None

* **Success Response:**
  * **Code:** 200 <br />
    **Content:** `{"data": {"1": ["controls-phosphorylation-of"], "2": ["reacts-with"],...}}`
 
* **Error Response:**
  * **Code:** 404 NOT FOUND <br />
    **Content:** `{"message" : "preference schedule not set" }`

**Code breakdown**
----
The code is organized into the following three classes, one utility file and a REST api:

*  **DirectedPaths**

    Responsible for processing the reference network and assembling the forward and reverse paths as well as the resulting subnetwork.

*  **PathScoring**

    Contains a nonparametric sorting algorithm that can be passed to a lambda expression for sorting
    
    For example: `sorted(results_list, lambda x,y: path_scoring.cross_country_scoring(x, y))`


*  **EdgeRanking**
    
    Contains the preference schedule for ranking edge types

    

*  **causal_utilities (utility file)**
    
    Contains method for:
     
    processing two way edge types - `indra_causality()`
    
    filtering edge types - `filter_edges()`
    
    shortest path finding - `k_shortest_paths_multi()`
    
    assembling a network from a set of paths - `network_from_paths()`
    

    

*  **runweb (REST api)**
    
    Contains REST api:
    
    