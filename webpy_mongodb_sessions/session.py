from datetime import datetime
from pymongo.binary import Binary
from re import _pattern_type
from time import time
from web.session import Store

seq_types = set((tuple, list))
map_types = set((dict,))
atomic_types = set((bool, int, long, float, str, unicode, type(None),
    _pattern_type, datetime))

def needs_encode(obj):
    '''
    >>> from re import compile
    >>> atomics = (True, 1, 1L, 1.0, '', u'', None, compile(''), datetime.now())
    >>> any(needs_encode(i) for i in atomics)
    False
    >>> needs_encode((1, 2, 3))
    False
    >>> needs_encode([])
    False
    >>> needs_encode([1, [2, 3]])
    False
    >>> needs_encode({})
    False
    >>> needs_encode({1: {2: 3}})
    False
    >>> needs_encode({(1,): [2]})
    False
    >>> needs_encode(set())
    True
    >>> needs_encode([1, [set()]])
    True
    >>> needs_encode({1: {2: set()}})
    True
    >>> needs_encode({frozenset(): 1})
    True
    '''
    obtype = type(obj)
    if obtype in atomic_types:
        return False
    if obtype in seq_types:
        return any(needs_encode(i) for i in obj)
    if obtype in map_types:
        return any(needs_encode(k) or needs_encode(v)
            for (k, v) in obj.iteritems())
    return True


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
    
    def encode(self, sessiondict):
        return dict((k, Binary(Store.encode(self, v)) if needs_encode(v) else v)
            for (k, v) in sessiondict.iteritems())

    def decode(self, sessiondict):
        return dict((k, Store.decode(self, v) if type(v) is Binary else v)
            for (k, v) in sessiondict.iteritems())

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

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
