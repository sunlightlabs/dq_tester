from pymongo import Connection
from settings import DATABASE_NAME
from tests_util import *

def year_over_year(db):
    programs = db['cfda'].find()
    for p in programs:
        if p.has_key('obligations'):
            obs = p['obligations']
            if obs:
                types = []
                for o in obs:
                    if o['assistance_type'] not in types: types.append(o['assistance_type'])

                for t in types:
                    grants = [l for l in sorted(obs, key=lambda k:['fiscal_year']) if l['assistance_type']==t]
                    first_year = None
                    count = 0
                    for o in grants:
                        if not first_year: 
                            first_year = o['fiscal_year']

                        if count == len(grants) - 1:
                            continue
                        
                        diff = grants[count + 1]['amount'] - o['amount']
                        if not o['amount']:
                            if not grants[count + 1]['amount']:
                                denom = 1
                            else:
                                denom = grants[count + 1]['amount']
                        else:
                            denom = o['amount']
                        
                        test_object = {}
                        

                        if float(diff) / denom > .5 or float(diff) / denom < -.5:
                            test_object['result'] = 'fail'
                        else: 
                            test_object['result'] = 'success'
                        #add data to test object
                        if p['recovery']:
                            test_object['result'] = 'warn'

                        test_object['fiscal_year'] = o['fiscal_year']
                        test_object['first_year'] = o['fiscal_year']
                        test_object['second_year'] = grants[count + 1]['fiscal_year']
                        test_object['percent_change'] = float(diff) / denom
                        test_object['assistance_type'] = t
                        p = add_test_result(p, 'year_over_year', test_object, ['fiscal_year', 'assistance_type'], [test_object['fiscal_year'], test_object['assistance_type']])
                        db['cfda'].save(p)
                    
                    #    print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (p.number, p.title, o.fiscal_year, o.amount, grants[count + 1].fiscal_year, grants[count + 1].amount, diff)

                        count += 1



if __name__ == "__main__":
    conn = Connection()
    db = conn[DATABASE_NAME]
    year_over_year(db) 
