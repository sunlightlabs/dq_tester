from tests_util import *
from pymongo import Connection

def under_minimum(db):
    programs = db['cfda'].find({"range_of_assistance.low": { '$exists': True }, "obligations": { '$exists': True }})
    for p in programs:
        for o in p["obligations"]:
            for r in p["range_of_assistance"]:
                if r['fiscal_year'] == o['fiscal_year'] or r['fiscal_year'] == 'no_year':
                    if o['amount'] < r['low']:
                        test_object = { 'result': 'fail',
                                        'fiscal_year': o['fiscal_year'],
                                      }
                        add_test_result(p, 'under_minimum', test_object, 'fiscal_year', o['fiscal_year'])
        db['cfda'].save(p)

if __name__ == "__main__":
    conn = Connection()
    db = conn[DB_NAME]
    under_minimum(db) 
