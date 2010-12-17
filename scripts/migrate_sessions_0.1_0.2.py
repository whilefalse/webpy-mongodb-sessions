#!/usr/bin/env python

from base64 import decodestring, encodestring
from pickle import dumps, loads
from pymongo import Connection
from pymongo.binary import Binary
from sys import argv, stdout, stderr
from webpy_mongodb_sessions.session import needs_encode

def main(dbname, collname='sessions'):
    db = getattr(Connection(), dbname)
    coll = getattr(db, collname)
    nsuccess = nfail = ntotal = 0
    migratedkey = '__migrated_0_1__0_2'
    for doc in coll.find({migratedkey: {'$exists': False}}):
        ntotal += 1
        docid = doc['_id']
        stdout.write('%4d. Migrating doc %s... ' % (ntotal, docid))
        try:
            data = doc['data']
            data = loads(decodestring(data))
            data = dict((k, Binary(encodestring(dumps(v))) if needs_encode(v)
                else v) for (k, v) in data.iteritems())
            coll.update({'_id': docid}, {'$set': {migratedkey: True,
                'data': data}}, safe=True)
        except Exception, e:
            nfail += 1
            stdout.write('fail\n')
            coll.update({'_id': docid}, {'$set': {migratedkey: 'failed: ' +
                str(e)}}, safe=True)
        else:
            nsuccess += 1
            stdout.write('ok\n')
    stdout.write('Done. %d sessions migrated, %d failed, %d total.\n' % (
        nsuccess, nfail, ntotal))
    if ntotal:
        stdout.write('You may want to run db.%s.update({}, {$unset: {%s: 1}}) '
            'if all went well.\n' % (collname, migratedkey))

if __name__ == '__main__':
    scriptname = argv.pop(0)
    try:
        dbname = argv.pop(0)
        collname = argv.pop(0)
    except IndexError:
        stderr.write('Usage: %s db_name collection_name\n' % scriptname)
        exit()
    main(dbname, collname)
