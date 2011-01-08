from settings import PROJECT_ROOT, DATABASE_NAME
from cfda.models import ASSIST_OPTIONS
from django.utils.encoding import smart_unicode
#from mongoengine.base import ValidationError
from pymongo import Connection
import csv
import re

#obligaton re's
re_funding = re.compile('FY ([0-1][0,1,6-9]{1,1})( est. | est | )[\$]([0-9,]+)')
re_funding_type = re.compile('\((.*?)\)')
re_exclude = re.compile('[sS]alaries')
re_direct = re.compile('payments')
re_grants = re.compile('grants|award|ship|agreement')
re_loan = re.compile('[lL]oan')
re_guar = re.compile('[gG]uarantee')
re_insur = re.compile('[iI]nsur|indemniti')
account = re.compile('[\d]{2}[-][\d]{4}[-][\d]{1}[-][\d]{1}[-][\d]{3}')
range_re = re.compile('((?:(?:FY\s?(\d{2,4})).*?)?' + \
                       '(?:([lL]oan|[gG]rant).*?)?' + \
                       '(?:\$?\s?((?:\d+(?:,|\.\d+)*(?:\s?(?:M|K|[M|m]illion))*)+)' + \
                           '(?:(?: to )|(?:\s*\-\s*))' + \
                          '\$?\s?((?:\d+(?:,|\.\d+)*(?:\s?(?:M|K|[M|m]illion))*)+))' + \
                        '|(?:[U|u]p to .*?(?:\$?\s?((?:\d+(?:,|\.\d+)*(?:\s?(?:M|K|[M|m]illion))*)+)))' + \
                        '|(?:(?:\$?\s?((?:\d+(?:,|\.\d+)*(?:\s?(?:M|K|[M|m]illion))*)+)) and up))')

number_text = re.compile('[mM]illion|M|K')
year_text = re.compile('\d{4}')

ob_assist_list = ( 
                    (re_direct, (3, 4, 7)),
                    (re_guar, (6,)),
                    (re_loan, (5,)),
                    (re_grants, (1, 2, 3, 4)),
                    (re_insur, (7,))
                )
 
VERSION = ''
logwriter = open("logs/cfda_import.log", 'a')

def get_or_create_program(number, db):
    prog = db.cfda.find_one({"number": number})
    if prog:
        return prog
    else:
        return { "number" : number }

def get_or_set_attr(obj, key, default=None):
    if obj.has_key(key):
        return obj
    else:
        obj[key] = default
        return obj

def match_ob_type_with_assistance(program, text):
    global ob_assist_list
    for re in ob_assist_list:
        if re[0].findall(text):
            program = get_or_set_attr(program, "assistance_types", [])
            for at in program["assistance_types"]:
                if at in re[1]:
                    return at


def add_assistance_type(program, code, db):
    program = get_or_set_attr(program, "assistance_types", [])
    if code not in program["assistance_types"]:    
        program["assistance_types"].append(code)
    db['cfda'].save(program)

def match_assistance(text):
    for type_tuple in ASSIST_OPTIONS:
        if text == type_tuple[1].lower() or type_tuple[2].findall(text):
            return type_tuple[0]

def parse_assistance(program, text, db):
    try:
        asst_types = smart_unicode(text).strip('.').split(';')
        for asst in asst_types:
            clean_asst = asst.lower().strip().replace("\n", "")
            code = match_assistance(clean_asst)
            if code:
                add_assistance_type(program, code, db)
            else:
                print "Assistance type didn't match for %s from program %s" % (text, program.title)
        
            #else:
             #   tester = text + " -----"
             #   for at in program.assistance_types:
             #       tester += ASSIST_OPTIONS[at-1][1]
             #   print tester
    except Exception, e:
        print str(e)

    return

def is_financial(program):
    financial = False
    program = get_or_set_attr(program, "assistance_types", [])
    for at in program["assistance_types"]:
        if at in [1, 2, 3, 4, 5, 6, 7, 8]:
            return True
    return False

def parse_obligation(program, ob_str, db):
    
    matches = re_funding.findall(ob_str)
    type_matches = re_funding_type.findall(ob_str)
    ob_type = ''
    curr_type = ''
    assist_code = ''
    curr_year = '2006'
    type_iter = iter(type_matches)

    if type_matches:
        curr_type = type_iter.next()
    for pair in matches:
        year = int('20' + pair[0])
        if year < curr_year:  #if the year sequence has started over, move to the next type
            try:
                curr_type = type_iter.next()
            except StopIteration:
                pass      #no more types
        curr_year = year
        obligation = int(pair[2].replace(",", ""))

        if (curr_type and re_exclude.findall(curr_type)) or not is_financial(program):
            continue  #leave out salaries and nonassistance stuff
        if curr_type:
            curr_type = curr_type.lower()
            assist_code = match_assistance(curr_type)
            if not assist_code:
                assist_code = match_ob_type_with_assistance(program, curr_type) # try and match with an assistance type already defined for this program
            if assist_code: ob_type = assist_code
        if not assist_code:                
            try:
                ob_type = program.assistance_types[0] #default it to first assistance type defined for program
            except Exception:
                ob_type = 1  # grants is always our default
        
        obligation = { "fiscal_year" : year, "amount" : obligation, "assistance_type" : ob_type}
        #check if this obligation exists
        program = get_or_set_attr(program, "obligations", [])
        already_in = False
        current_ob = None

        for o in program["obligations"]:
            if o['fiscal_year'] == year and o['assistance_type'] == ob_type: 
                already_in = True
                current_ob = o
                break

        if already_in:
            if program.has_key("run") and program["run"] < VERSION:
                current_ob["amount"] = obligation["amount"]
                db['cfda'].save(program)
        else:
            program["obligations"].append(obligation)
            db['cfda'].save(program)
        
        db['cfda'].save(program)

def parse_budget_account(program, account_text):
    matches = account.findall(account_text)
    for match in matches:
        agency_code = match[0:2]
        account_symbol = match[3:7]
        transmittal_code = match[8]
        fund_code = match[10]
        subfunction_code = match[12:]
        ba = { "code": match, "agency_code" : agency_code, "fund_code" : fund_code, "subfunction_code" : subfunction_code, "transmittal_code" : transmittal_code, "account_symbol" : account_symbol}
        
        already_in = False
        program = get_or_set_attr(program, "budget_accounts", [])
        for acc in program["budget_accounts"]:
            if match == acc['code']:
                already_in = True
                break

        if not already_in:
            program["budget_accounts"].append(ba)


def convert_text_to_number(text):
    if re.findall('\d{4}', text):
        number = None
    elif re.findall('[mM]illion|M', text):
        number = float(text.strip().lower().replace(' ', '').replace(',', '').replace('million', '').replace('m', '')) * 1000000
    elif re.findall('K|k', text):
        number = float(text.strip().lower().replace(' ', '').replace(',', '').replace('k', '').replace('thousand', '')) * 1000
    elif re.findall('\.\d{3}', text):
        number = float(text.strip().lower().replace(' ', '').replace(',', '').replace('.', ''))  #typo, period should be comma
    elif re.findall('\.\d{1}', text):
        number = None  #invalid if not shorthand and not cents
    else:
        number = float(text.strip().lower().replace(' ', '').replace(',', ''))
    return number

def parse_obligation_range(program, text, db):
    matches = range_re.findall(text)
    for m in matches:
        #assign groups to respective vars
        full_match, fiscal_year, spending_type, range_low, range_high, max_range, min_range = m
        if (range_low and range_high) or max_range or min_range:
            #we have usable(maybe) data
            range_data = {}
            if fiscal_year:
                range_data['fiscal_year'] = fiscal_year
            else:
                range_data['fiscal_year'] = 'no_year'
            if spending_type:
                range_data['type'] = spending_type.strip()
            if max_range:
                range_data['low'] = 0
                range_data['high'] = convert_text_to_number(max_range)
                if not range_data['high']: continue
            elif min_range:
                range_data['low'] = convert_text_to_number(min_range)
                range_data['high'] = 'no max'
                if not range_data['low']: continue
            elif range_low and range_high:
                range_low = convert_text_to_number(range_low)
                range_high = convert_text_to_number(range_high)
                if range_low and range_high:
                    if range_low < 100 and range_high < 100:
                        logwriter.write("Possible range mistake. Program: %s\tRange Match:%s\n" % (program['number'], full_match))
                        continue
                    range_data['low'] = range_low
                    range_data['high'] = range_high
                else:
                    continue
            else:
                continue

            #parse out the average somewhere

            if program.has_key('range_of_assistance'):
                for r in program['range_of_assistance']:
                    if r['fiscal_year'] == range_data['fiscal_year']:
                        program['range_of_assistance'].remove(r)
                        program['range_of_assistance'].append(range_data)
                        db['cfda'].save(program)
                        return
                program['range_of_assistance'].append(range_data)
            else:
                program['range_of_assistance'] = [range_data]
            
              # print m
    db['cfda'].save(program)

def get_agency(program, program_number, db):
    agency = db['agency'].find_one({"cfda_code" : program_number[:2]})
    if agency:
        a = {"cfda_code": agency["cfda_code"], "treasury_code": agency["treasury_code"], "name" : agency["name"]}
        program["agency"] = a
        db["cfda"].save(program)


def parse_cfda_line(row, db):

    program_title = smart_unicode(row[0], errors='ignore')
    program_number = smart_unicode(row[1], errors='ignore')
    assistance_type = smart_unicode(row[6], errors='ignore')
    obligations_text = smart_unicode(row[24], errors='ignore')
    account_text = smart_unicode(row[23], errors='ignore')
    range_text = smart_unicode(row[25], errors='ignore')
    recovery = smart_unicode(row[37], errors='ignore')
    program  = get_or_create_program(program_number.strip(), db)
    program["title"] = program_title
    parse_assistance(program, assistance_type, db)
    parse_obligation(program, obligations_text, db)
    parse_budget_account(program, account_text)
    parse_obligation_range(program, range_text, db)

    get_agency(program, program_number, db)
    if recovery.strip().lower() == 'yes':
        program['recovery'] = True
    else:
        program['recovery'] = False
    program["run"] = VERSION
    db['cfda'].save(program)

def get_or_create_subagency(name, agency, db):
    sa = db['subagency'].find_one({"name" : name})
    if sa:
        return sa
    else:
        sa = { "name": name, "agency" : agency }
        db['subagency'].save(sa)
        return sa

def parse_subagencies(line, db):
    program_num = smart_unicode(line[0], errors='ignore')
    office = smart_unicode(line[2], errors='ignore')
    if office.find('/') > -1:
        program = db['cfda'].find_one({ "number" : program_num})
        if not program:
            print "Program %s not found!" % program_num
            return  
        name = office.split("/")[1].strip()
        sa = db["subagency"].find_one({ "name" : name })
        if sa:
            program["subagency"] = sa        
        else:
            if program.has_key("agency"):
                sa = get_or_create_subagency(name, program["agency"], db)
            else:
                agency = db['agency'].find_one({"name": office.split("/")[0].strip() })
                if agency:
                    sa = get_or_create_subagency(name, agency, db)
                else:
                    pass
                    #log  to error file
        db['cfda'].save(program)
                
def load_cfda(file_name):
    try:
        reader = csv.reader(open(file_name))

    except IOError:
        try:
            reader = csv.reader(open("%s/data/%s" % (PROJECT_ROOT, file_name)))
        except IOError:
            print "csv file not found in data dir"
            return

        print "csv file not found"
        return
    global VERSION
    VERSION = file_name[-9:-4]
    conn = Connection()
    db = conn[DATABASE_NAME]
    reader.next()
    for row in reader:
        parse_cfda_line(row, db)

    reader_sa = csv.reader(open("%s/data/cfda_programs_by_agency_subagency.csv" % PROJECT_ROOT))
    reader_sa.next()
    for line in reader_sa:
        parse_subagencies(line, db)

    db['cfda'].ensure_index("program_number", unique=True)

