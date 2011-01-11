from django.shortcuts import render_to_response
from django.conf import settings

db = settings.DB_CONNECTION

def agency(request, cfda_id):
    agency = db['agency'].find_one({'cfda_code': str(cfda_id)})
    programs = db['cfda'].find({'agency.cfda_code':str(cfda_id)})
    data = get_list(programs)
    return render_to_response('agency.html', {"programs": data, 'agency': agency })

def failed(request):
    programs = db['cfda'].find({'tests.fail': { '$exists':True}})
    data = get_list(programs)
    return render_to_response('list.html', {'programs': data, "title": "Failed Programs", "type": "failed" })

def nottested(request):
    programs = db['cfda'].find({'tests': { '$exists':False}})
    data = get_list(programs)
    return render_to_response('list.html', {'programs': data, "title": "Programs with Insufficient Data to be Tested", "type": "nottested" })

def get_list(programs):
    data = []
    for p in programs:
        if p.has_key('tests'):
            if p['tests'].has_key('success'):
                p['success_total'] = len(p['tests']['success'])
                p['css_class'] = 'success'
            if p['tests'].has_key('warn'):
                p['warned_total'] = len(p['tests']['warn'])
                p['css_class'] = 'warn'
            if p['tests'].has_key('fail'):
                p['failed_total'] = len(p['tests']['fail'])
                p['css_class'] = 'fail'

            p['tested'] = True
        else:
            p['tested'] = False
            p['css_class'] = 'neutral'

        data.append(p)

    return data

