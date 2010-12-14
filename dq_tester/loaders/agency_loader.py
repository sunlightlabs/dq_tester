from agency.models import Subagency, Agency, AGENCY_MAP
from pymongo import Connection
from settings import DB_NAME

conn = Connection()
db = conn[DB_NAME]

def get_or_create_agency(treasury_code):
    a = db['agency'].find_one({"treasury_code": treasury_code})
    if not a:
        return {"treasury_code" : treasury_code}
    else:
        return a

def load_agencies():
    #load agencies into db
    for k in AGENCY_MAP.keys():
        agency = get_or_create_agency(AGENCY_MAP[k][0])
        agency["cfda_code"] = k
        agency["name"] = AGENCY_MAP[k][1].lower().strip()
        db["agency"].save(agency)

    db['agency'].ensure_index("treasury_code", unique=True)
    db['agency'].ensure_index("cfda_code", unique=True)



    
