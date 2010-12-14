from web.session import Store
from time import time

#: field name used for id
_id = '_id'
#: field name used for accessed time
_atime = 'atime'
#: field name used for data
_data = 'data'

class MongoStore(Store):
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
        self.collection.ensure_index(_atime)
    
    def __contains__(self, key):
        return bool(self.collection.find_one({_id: key}))

    def __getitem__(self, key):
        s = self.collection.find_one({_id: key})
        if not s:
            raise KeyError(key)
        self.collection.update({_id: key}, {'$set': {_atime: time()}}, safe=True)
        return self.decode(s[_data])

    def __setitem__(self, key, value):
        data = self.encode(value)
        self.collection.save({_id: key, _data: data, _atime: time()}, safe=True)

    def __delitem__(self, key):
        self.collection.remove({_id: key}, safe=True)

    def cleanup(self, timeout):
        '''
        Removes all sessions older than ``timeout`` seconds.
        Called automatically on every session access.
        '''
        cutoff = time() - timeout
        self.collection.remove({_atime: {'$lt': cutoff}})
