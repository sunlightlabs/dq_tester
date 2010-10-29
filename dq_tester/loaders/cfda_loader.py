from cfda.models import *
from agency.models import Agency as ExtAgency
from settings import PROJECT_ROOT
from django.utils.encoding import smart_unicode
from mongoengine.base import ValidationError
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

ob_assist_list = ( 
                    (re_direct, (3, 4, 7)),
                    (re_guar, (6,)),
                    (re_loan, (5,)),
                    (re_grants, (1, 2, 3, 4)),
                    (re_insur, (7,))
                )
 
VERSION = ''

def get_or_create_program(number):
    prog = Program.objects(number=number)
    if prog:
        return prog[0]
    else:
        return Program(number=number)

def match_ob_type_with_assistance(program, text):
    global ob_assist_list
    for re in ob_assist_list:
        if re[0].findall(text):
            for at in program.assistance_types:
                if at in re[1]:
                    return at


def add_assistance_type(program, code):
    if not program.assistance_types:
        program.assistance_types = [code]
    elif code not in program.assistance_types:    
        program.assistance_types.append(code)
    program.save()

def match_assistance(program, text):
    for type_tuple in ASSIST_OPTIONS:
        if text == type_tuple[1].lower() or type_tuple[2].findall(text):
            return type_tuple[0]

def parse_assistance(program, text):
    try:
        asst_types = smart_unicode(text).strip('.').split(';')
        for asst in asst_types:
            clean_asst = asst.lower().strip().replace("\n", "")
            code = match_assistance(program, clean_asst)
            if code:
                add_assistance_type(program, code)
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
    if program.assistance_types:
        for at in program.assistance_types:
            if at in [1, 2, 3, 4, 5, 6, 7, 8]:
                return True
    return False

def parse_obligation(program, ob_str):
    
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
        year = '20' + pair[0]
        if year < curr_year:  #if the year sequence has started over, move to the next type
            try:
                curr_type = type_iter.next()
            except StopIteration:
                pass      #no more types
        curr_year = year
        obligation = pair[2].replace(",", "")

        if (curr_type and re_exclude.findall(curr_type)) or not is_financial(program):
            continue  #leave out salaries and nonassistance stuff
        if curr_type:
            curr_type = curr_type.lower()
            assist_code = match_assistance(program, curr_type)
            if not assist_code:
                assist_code = match_ob_type_with_assistance(program, curr_type) # try and match with an assistance type already defined for this program
            if assist_code: ob_type = assist_code
        if not assist_code:                
            try:
                ob_type = program.assistance_types[0] #default it to first assistance type defined for program
            except Exception:
                ob_type = 1  # grants is always our default
        
        obligation = Obligation(fiscal_year=year, amount=obligation, assistance_type=ob_type)
        # check to see if this obligation exists
        if program.obligations and obligation in program.obligations:
            if program.run < VERSION:
                program.obligations.get(fiscal_year=year, assistance_type=ob_type).amount=obligation
                program.save()
        elif not program.obligations:
            program.obligations = [obligation]
            program.save()
        else:
            program.obligations.append(obligation)
            program.save()

        program.save()

def parse_budget_account(program, account_text):
    matches = account.findall(account_text)
    for match in matches:
        print match
        agency_code = int(match[0:2])
        account_symbol = int(match[3:7])
        transmittal_code = int(match[8])
        fund_code = int(match[10])
        subfunction_code = int(match[12:])
        ba = BudgetAccount(code=match, agency_code=agency_code, fund_code=fund_code, subfunction_code=subfunction_code, transmittal_code=transmittal_code, account_symbol=account_symbol)
        
        already_in = False
        for acc in program.budget_accounts:
            if match == acc['code']:
                already_in = True
                break

        if not already_in:
            if not program.budget_accounts:
                program.budget_accounts = [ba]
            else:
                program.budget_accounts.append(ba)

def get_agency(program, program_number):
    agency = ExtAgency.objects.get(cfda_code=program_number[:2])
    if not program.agency:
        a = Agency(cfda_code=agency.cfda_code, treasury_code=agency.treasury_code, name=agency.name)
        program.agency = a
        program.save()

def parse_cfda_line(row):

    program_title = smart_unicode(row[0], errors='ignore')
    program_number = smart_unicode(row[1], errors='ignore')
    assistance_type = smart_unicode(row[6], errors='ignore')
    obligations_text = smart_unicode(row[24], errors='ignore')
    account_text = smart_unicode(row[23], errors='ignore')
    range_text = smart_unicode(row[25], errors='ignore')

    program  = get_or_create_program(program_number.strip())
    program.title = program_title
    parse_assistance(program, assistance_type)
    parse_obligation(program, obligations_text)
    parse_budget_account(program, account_text)
    get_agency(program, program_number)
#    for i in program.__dict__.keys():
#        print "%s : %s" % (i, program.__dict__[i])
    program.run = VERSION
    program.save()

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
    reader.next()
    for row in reader:
        parse_cfda_line(row)



