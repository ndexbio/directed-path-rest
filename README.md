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
The code is organized into the following classes:

*  **DirectedPaths**

*  **PathScoring**

*  **EdgeRanking**

Also the following utility file:

*  **causal_utilities**