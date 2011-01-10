from django.shortcuts import render_to_response
from django.conf import settings
from cfda.models import ASSIST_OPTIONS
db = settings.DB_CONNECTION

def index(request):
    data = []
    agencies = db['agency'].find().sort("name")
    for a in agencies:
        programs = db['cfda'].find({"agency.cfda_code": a['cfda_code']}).sort("name")
        failed_total = 0
        warned_total = 0
        success_total = 0
        notest_total = 0
        total = 0
        for p in programs:
            total += 1
            if p.has_key('tests') and p['tests'].has_key('fail'):
                failed_total += 1        
            elif p.has_key('tests') and p['tests'].has_key('warn'):
                warned_total += 1        
            elif p.has_key('tests') and not p.has_key('fail') and not p.has_key('warn'):
                success_total += 1
            if not p.has_key('tests'):
                notest_total += 1

        a['success_total'] = success_total
        a['failed_total'] = failed_total
        a['warned_total'] = warned_total
        a['notest_total'] = notest_total
        a['program_total'] = total

        data.append(a)
    return render_to_response('index.html', {"agencies": data})


def get_obligation_for_year(program, year, assistance_type):
    for o in program['obligations']:
        if o['fiscal_year'] == year and o['assistance_type'] == assistance_type:
            return o['amount']

def cfda(request, number):
    prog = db['cfda'].find_one({'number': number})
    tests = {}
    if prog.has_key('tests'):
        for result in prog['tests'].keys():
            for t in prog['tests'][result]:
                if t['name'] == 'year_over_year':
                    t['first_year_ob'] = get_obligation_for_year(prog, t['first_year'], t['assistance_type'])
                    t['second_year_ob'] = get_obligation_for_year(prog, t['second_year'], t['assistance_type'])
                    t['percent_change'] = t['percent_change'] * 100
                    for at in ASSIST_OPTIONS:
                        if t.has_key('assistance_type') and at[0] == t['assistance_type']:
                            t['assistance_type'] = at[1]

                elif t['name'] == 'under_minimum' or t['name'] == 'under_maximum':
                    for roa in prog['range_of_assistance']:
                        if roa['fiscal_year'] == 'no_year' or roa['fiscal_year'] == t['fiscal_year']:
                            t['range_of_assistance_low'] = roa['low']
                            t['range_of_assistance_high'] = roa['high']

                    t['obligation'] = get_obligation_for_year(prog, t['fiscal_year'], t['assistance_type'])

                if tests.has_key(t['name']):
                    tests[t['name']].append(t)
                else:
                    tests[t['name']] = [t]


    test_array = []
    for k in tests.keys():
        d = [k.replace('_', ' ')]
        d.extend(tests[k])
        test_array.append(d)
    
    return render_to_response('program.html', {"program": prog, 'tests': test_array})
