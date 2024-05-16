from flask import Flask, jsonify, request
from jsonexus import JSONexus
from secrets import token_urlsafe
from hashlib import sha256

app = Flask(__name__)
db = JSONexus('.etc/db.json')

class execute_query:
    def __init__(self, query):
        self.query = query
        self.operations = {
            'find': db.find,
            'insert': db.insert,
            'delete': db.delete,
            'update': db.update,
            'count': db.count,
            'find_one': db.find_one,
            'get_all': db.get_all,
            'get_collection': db.get_collection,
            'create_collection': db.create_collection
        }
    def validate_query(self, query):
        if isinstance(query, dict) and len(query) == 1:
            for (col_name, operations_dict) in query.items():
                if list(operations_dict.items())[0][0] in self.operations:
                    if len(operations_dict) == 1:
                        for (operation, _qry) in operations_dict.items():
                            if operation == 'update' and isinstance(_qry,
                                    dict) and len(_qry) == 2:
                                return True
                        return True
        return False
    def execute(self):
        if not self.validate_query(self.query):
            return None
        results = []
        for col_name, operations_dict in self.query.items():
            for operation, _qry in operations_dict.items():
                if operation == 'update':
                    _qry, _updated = _qry
                try:
                    _op = self.operations[operation]
                    if operation == 'get_collection' or operation == 'count':
                        results.append(_op(col_name))
                    elif operation == 'update':
                        results.append(_op(col_name, _qry, _updated))
                    elif operation == 'get_all':
                        result = _op()
                        results.append(result)
                    elif operation == 'create_collection':
                        results.append(_op(_qry['name']))
                    else:
                        results.append( _op(col_name, _qry))
                except KeyError as e:
                    return {'error': f'invalid collection {e}'}

        return results if results else None  # Return results or None

if db.count('api')==0:
    print('No API key found. Generating new one...')
    api_key = token_urlsafe(64)
    print('New API key:', api_key, "\nSave it somewhere safe!")
    db.insert('api',{'key':sha256(api_key.encode()).hexdigest()})

@app.route('/api', methods=['POST'])
def api():
    if "X-API-KEY" not in request.headers:
        return jsonify({"error": "Missing API key"})
    
    client_api_key = sha256(request.headers["X-API-KEY"].encode()).hexdigest()
    if client_api_key != db.find_one('api', {'key': client_api_key})['key']:
        return jsonify({"error": "Invalid API key"})
    
    query = request.get_json()
    if not query:
        return jsonify({"error": "Missing query"})
    
    return execute_query(query).execute()

if __name__ == '__main__':
    app.run(debug=True)
        
    