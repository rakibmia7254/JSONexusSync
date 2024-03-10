JSONexusSync Documentation
==========================

Introduction
------------

JSONexusSync is a cutting-edge remote database system designed for seamless data synchronization over WebSockets. Built upon the robust JSONexus platform, JSONexusSync offers a streamlined solution for real-time data storage and retrieval across distributed systems.

Features
--------

*   Efficient data synchronization over WebSockets
*   Real-time updates and data consistency
*   Intuitive interface for developers
*   Scalable solution for remote data management

Usage
-----

To use JSONexusSync, developers need to integrate the client-side library into their applications and connect to the remote database server. From there, they can perform CRUD (Create, Read, Update, Delete) operations seamlessly and receive real-time updates.

Getting Started
---------------

### 1. Get JSONexusSync
To Downlaod JSONexusSync, follow these steps:

    $ git clone https://github.com/rakibmia7254/JSONexusSync



### 2. Start Server
Start JSONexusSync server in your project Directory.

    $ python main.py

    Initializing the databases...
    Initializing Web Server...
    tarting the WebSocket server...
    WebSocket server started on localhost:8765


### 3. Create a Database.
To create a database, you need to send a request to the server and include the database name.
```python
import asyncio
import websockets

async def main(db_name):
    uri = "ws://localhost:8765"  # WebSocket server address

    async with websockets.connect(uri) as websocket:
        # Send your request here
        request = {
            'method': 'create_db', 
            'db': db_name
            } #request payload
        await websocket.send(request)
        # Receive the response
        response = await websocket.recv()
        print("Response:", response)

database_name = "my_app_database"
asyncio.get_event_loop().run_until_complete(main(database_name))


```


### 4. Generating api-key
To generate an API key, you need to send another request to the server, including the `user` name and which `database` the user can access.

```python 

import websockets

async def main(user, database):
    uri = "ws://localhost:8765"  # WebSocket server address

    async with websockets.connect(uri) as websocket:
        # Send your request here
        request = {
            'method': 'generate_api_key', 
            'name': user, 
            'db': database
            } #request payload
        await websocket.send(request)
        # Receive the response
        response = await websocket.recv()
        print("Response:", response)

user_name = 'admin'
database_name = 'my_app_database'
asyncio.get_event_loop().run_until_complete(main(user_name, database_name))
```

Example (Python)
----------------

Below is an example of sending WebSocket requests using Python:


### 1. insering data
```python

import asyncio
import websockets

async def main(api_key, collection_name, data_to_insert):
    uri = "ws://localhost:8765"  # WebSocket server address

    async with websockets.connect(uri) as websocket:
        # Prepare data to send
        request = {
            'api_key': api_key,
            "method": "insert",
            "collection_name": collection_name,
            "data": data_to_insert
        }

        # Send the request
        await websocket.send(request)

        # Receive the response
        response = await websocket.recv()
        print("Response:", response)

api_key = "YourApiKey"
database_name = "users"
data_to_insert = {
    'name': 'Charlie', 
    'age': 35, 
    'email': 'charlie@example.com'
}

asyncio.get_event_loop().run_until_complete(main(database_name, data_to_insert))


```
            

Conclusion
----------

JSONexusSync offers a reliable and scalable solution for remote data management, making it an ideal choice for developers looking to synchronize data across distributed systems efficiently.

For more information and detailed documentation, please visit the [JSONexusSync Documentation](https://jsonexus.gitbook.io/jsonexussync/).