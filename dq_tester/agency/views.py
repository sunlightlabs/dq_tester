from django.shortcuts import render_to_response
from django.conf import settings

db = settings.DB_CONNECTION

def agency(request, cfda_id):
    data = []
    agency = db['agency'].find_one({'cfda_code': str(cfda_id)})
    programs = db['cfda'].find({'agency.cfda_code':str(cfda_id)})
    for p in programs:
        if p.has_key('tests'):
            if p['tests'].has_key('fail'):
                p['failed_total'] = len(p['tests']['fail'])
            if p['tests'].has_key('warn'):
                p['warned_total'] = len(p['tests']['warn'])
            if p['tests'].has_key('success'):
                p['success_total'] = len(p['tests']['success'])

            p['tested'] = True
        else:
            p['tested'] = False

        data.append(p)

    return render_to_response('agency.html', {"programs": data, 'agency': agency })

    
