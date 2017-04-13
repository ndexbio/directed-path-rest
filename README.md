directed-path-rest
===========

REST service for finding directed paths in a reference network.

**BOLD**


## REST API

**Directed path search**
----
  Returns json data .

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

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error : "User doesn't exist" }`

  OR

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{ message : "Missing source list in query string." }`

