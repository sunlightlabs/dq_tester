from agency.models import Subagency, Agency, AGENCY_MAP
from mongoengine.base import ValidationError



def load_agencies():
    #load agencies into db
    for k in AGENCY_MAP.keys():
        agency = Agency.objects.get_or_create(cfda_code=k)
        agency.treasury_code = AGENCY_MAP[k][0]
        agency.name = AGENCY_MAP[k][1]
        agency.save()




    
