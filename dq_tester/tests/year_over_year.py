from cfda.models import *
from mongoengine import StringField
from pymongo import Connection
from settings import DB_NAME
from tests_util import *

def year_over_year(db):
    programs = db['cfda'].all()
    for p in programs:
        obs = p['obligations']
        if obs:
            first_year = None
            count = 0
            grants = [l for l in sorted(obs, key=lambda k:['fiscal_year']) if l['assistance_type'] in [1, 2, 3, 4]]
            for o in grants:
                if not first_year: 
                    first_year = o['fiscal_year']
                if count == len(grants) - 1:
                    continue
                
                diff = grants[count + 1]['amount'] - o['amount']
                if not o['amount']:
                    denom = 1
                else:
                    denom = o['amount']
                if float(diff) / denom > .5 or float(diff) / denom < -.5:
                    test_object = {}

                    #add data to test object

                    p = add_test_result(p, 'year_over_year', test_object)

                    o['flag_year_1'] = True
                    grants[count + 1]['flag_year_2'] = True
                    p['tester'] = StringField('test')
                    p.save()
               
               #    print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (p.number, p.title, o.fiscal_year, o.amount, grants[count + 1].fiscal_year, grants[count + 1].amount, diff)

                count += 1



if __name__ == "__main__":
    conn = Connection()
    db = conn[DB_NAME]
    year_over_year(db) 
