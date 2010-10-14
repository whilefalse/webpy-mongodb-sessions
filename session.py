from web.session import Store
import time

# XXX made the following modifications:
# - use Store.encode/decode so we can store python objects
# - use session_id as object ids
# - use collection.update instead of save
# - use safe=True for insert/update/remove
class MongoStore(Store):
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def __contains__(self, key):
        return bool(self.collection.find_one({'_id': key}))

    def __getitem__(self, key):
        now = time.time()
        s = self.collection.find_one({'_id': key})
        if not s:
            raise KeyError
        self.collection.update({'_id': key}, {'$set': {'attime': now}}, safe=True)
        return self.decode(s['data'])

    def __setitem__(self, key, value):
        now = time.time()
        data = self.encode(value)
        if self.collection.find_one({'_id': key}):
            self.collection.update({'_id': key}, {'$set': {'data': data, 'attime': now}}, safe=True)
        else:
            self.collection.insert({'_id': key, 'data': data, 'attime': now}, safe=True)
                
    def __delitem__(self, key):
        self.collection.remove({'_id': key})

    def cleanup(self, timeout):
        timeout = timeout/(24.0*60*60) #timedelta takes numdays as arg
        last_allowed_time = time.time() - timeout
        self.collection.remove({'attime' : { '$lt' : last_allowed_time}})
