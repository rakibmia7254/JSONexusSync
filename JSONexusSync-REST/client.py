from jsonexussync_client.RestClient import JSONexusSyncClient as client

db = client({
            "api_key": "VzM3eJ9I_TFThTAppN4Zxtgl5E9vEqv_qvzqRdZD_c3_JVxNDJKlt9LjbKd4DpF1ruWrtE84R4M5Wl_RMbouyw",
             "server_uri": "http://127.0.0.1:5000/api"})

# print(db.get_collection('fake'))
print(db.find_one('fake', {'name': 'Denise Warren'}))