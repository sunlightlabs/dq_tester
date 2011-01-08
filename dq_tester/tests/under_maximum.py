from tests_util import *
from django.conf import settings
from pymongo import Connection

def under_maximum(db):
    programs = db['cfda'].find({"range_of_assistance.high": { '$exists': True }, "obligations": { '$exists': True }})
    for p in programs:
        for o in p["obligations"]:
            for r in p["range_of_assistance"]:
                if r['fiscal_year'] == o['fiscal_year'] or r['fiscal_year'] == 'no_year':
                    if o['amount'] < r['high']:
                         test_object = { 'result': 'warn',
                                        'fiscal_year': o['fiscal_year'],
                                      }
                         add_test_result(p, 'under_maximum', test_object, 'fiscal_year', o['fiscal_year'])
        db['cfda'].save(p)

if __name__ == "__main__":
    conn = Connection()
    db = conn[DATABASE_NAME]
    under_maximum(db) 
