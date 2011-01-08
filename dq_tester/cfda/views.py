from django.shortcuts import render_to_response
from django.conf import settings

db = settings.DB_CONNECTION

def index(request):
    data = []
    agencies = db['agency'].find().sort("name")
    for a in agencies:
        programs = db['cfda'].find({"agency.cfda_code": a['cfda_code']}).sort("name")
        failed_total = 0
        warned_total = 0
        success_total = 0

        for p in programs:
            if p.has_key('tests') and p['tests'].has_key('fail'):
                failed_total += 1        
            if p.has_key('tests') and p['tests'].has_key('warn'):
                warned_total += 1        
            if p.has_key('tests') and not p.has_key('fail') and not p.has_key('warn'):
                success_total += 1

        a['success_total'] = success_total
        a['failed_total'] = failed_total
        a['warned_total'] = warned_total
        data.append(a)
    return render_to_response('index.html', {"agencies": data})
