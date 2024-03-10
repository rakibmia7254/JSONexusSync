import asyncio
import websockets
import json
import jsonexus
import os
from hashlib import md5

print("Initializing the databases...")

# Check if the .etc and .databases folders exist
if not os.path.exists('.etc'):
    os.mkdir('.etc')
if not os.path.exists('.databases'):
    os.mkdir('.databases')
jsonexus.JSONexus
# Initialize the databases
dbs = jsonexus.JSONexus('.etc/db_list.json')
datbase_conent = {}
if 'dbs' not in dbs.get_collections():
    dbs.create_collection('dbs')
for db in dbs._read_db()['dbs']:
    if 'name' in db and 'path' in db:
         datbase_conent[db['name']] = jsonexus.JSONexus(db['path'])
    else:
        pass

print("Initializing Web Server...")

# Socket Server
class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        api_db = jsonexus.JSONexus('.etc/apis.json')
        if 'api_keys' not in api_db.get_collections():
            api_db.create_collection('api_keys')
        self.apis = api_db

    async def handle_connection(self, websocket, path):
        try:
            async for message in websocket:
                request_data = json.loads(message)
                api_key = request_data.get('api_key')
                if api_key is None:
                    if request_data.get('method') == 'generate_api_key':
                        api_name = request_data.get('name')
                        db_allowed = request_data.get('db')
                        print('LOG: API key requested for {} in {}'.format(api_name, db_allowed))
                        if db_allowed in datbase_conent.keys():
                            apis_content = {'name': api_name, 'db': db_allowed}
                            apis_content['key'] = md5(str(apis_content).encode('utf-8')).hexdigest()
                            if self.apis.find('api_keys', {"name":{'_op': '$eq', '_value': api_name}})['result'] == []:
                                self.apis.insert('api_keys', apis_content)
                                await websocket.send(json.dumps({"status": "success", "key": apis_content['key']}))
                            else:
                                await websocket.send(json.dumps({"status": "failed", "message": "API name already exists"}))
                        else:
                            await websocket.send(json.dumps({"status": "failed", "message": "Database not found"}))
                    elif request_data.get('method') == 'create_db':
                        db_name = request_data.get('db')
                        print('LOG: Database {} requested'.format(db_name))
                        if db_name not in datbase_conent.keys():
                            db_path = '.databases/'+db_name+os.urandom(5).hex()+'.json'
                            datbase_conent[db_name] = jsonexus.JSONexus(db_path)
                            dbs.insert('dbs', {'name': db_name, 'path': db_path})
                            await websocket.send(json.dumps({"status": "success", "name": db_name}))
                        else:
                            await websocket.send(json.dumps({"status": "failed", "message": "Database already exists"}))
                    else:
                        await websocket.send(json.dumps({"status": "failed", "message": "Invalid Method"}))
                
                api_check = self.apis.find('api_keys', {'key':{'_op': '$eq', '_value': api_key}})
                # Check if the API key is valid
                if api_check['result'] != []:
                    db = datbase_conent[api_check['result'][0]['db']]
                    method = request_data.get('method')
                    if method == 'insert':
                        collection_name = request_data.get('collection_name')
                        data = request_data.get('data')
                        print("LOG: {} inserted into '{}'".format(data, collection_name))
                        await websocket.send(json.dumps(db.insert(collection_name, data)))
                    elif method == 'insert_many':
                        collection_name = request_data.get('collection_name')
                        data = request_data.get('data')
                        print("LOG: inserted many into '{}'".format(collection_name))
                        await websocket.send(json.dumps(db.insert_many(collection_name, data)))
                    elif method == 'create_collection':
                        collection_name = request_data.get('collection_name')
                        print("LOG: '{}' created".format(collection_name))
                        await websocket.send(json.dumps(db.create_collection(collection_name)))
                    elif method == 'get_dbs':
                        print("LOG: requested Datbases Names")
                        db_list = []
                        for db in dbs.get_all()['dbs']:
                            db_list.append(db['name'])
                        response = {'dbs': db_list}
                        await websocket.send(json.dumps(response))
                    elif method == 'find':
                        collection_name = request_data.get('collection_name')
                        query = request_data.get('query')
                        print("LOG: '{}' found in '{}'".format(query, collection_name))
                        result = db.find(collection_name, query)
                        await websocket.send(json.dumps(result))
                    elif method == 'match':
                        collection_name = request_data.get('collection_name')
                        query = request_data.get('query')
                        print("LOG: '{}' matched in '{}'".format(query, collection_name))
                        result = db.match(collection_name, query)
                        await websocket.send(json.dumps(result))
                    elif method == 'update':
                        collection_name = request_data.get('collection_name')
                        query = request_data.get('query')
                        update_fields = request_data.get('update_fields')
                        print("LOG: '{}' updated in '{}'".format(update_fields, collection_name))
                        await websocket.send(json.dumps(db.update(collection_name, query, update_fields)))
                    elif method == 'delete':
                        collection_name = request_data.get('collection_name')
                        query = request_data.get('query')
                        print("LOG: '{}' deleted in '{}'".format(query, collection_name))
                        await websocket.send(json.dumps(db.delete(collection_name, query)))
                    elif method == 'list_db':
                        await websocket.send(json.dumps(datbase_conent))
                    else:
                        await websocket.send(json.dumps({"error": "Invalid method"}))
                else:
                    await websocket.send(json.dumps({"error": "Invalid API key"}))
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed")

    def start(self):
        print("Starting the WebSocket server...")
        start_server = websockets.serve(self.handle_connection, self.host, self.port)
        print(f"WebSocket server started on {self.host}:{self.port}")
        print("Press Ctrl+C to stop the server")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    server = WebSocketServer('localhost', 8765)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Stopping the WebSocket server...")