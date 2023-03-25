import urllib3
http = urllib3.PoolManager()

fields_data = {
    'city': 'Delhi',
    'coordinates': '[23, 35]',
    'level': 'High',
    'nature': 'Murder',
    'reported': 'Chowki 6'
};

r = http.request('POST', 'http://172.16.42.54:5000/put',
                 fields=fields_data)
