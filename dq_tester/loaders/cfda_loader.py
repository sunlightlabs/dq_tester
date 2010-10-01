from cfda.models import *
from settings import PROJECT_ROOT, DATABASE_NAME
from django.utils.encoding import smart_unicode
from mongoengine.base import ValidationError
from mongoengine import connect
import csv

connect(DATABASE_NAME)

def get_or_create_program(number):
    prog = Program.objects(_id=number)
    if prog:
        return prog[0]
    else:
        return Program(_id=number)

def parse_cfda_line(row, version):

    program_title = smart_unicode(row[0], errors='ignore')
    program_number = smart_unicode(row[1], errors='ignore')
    obligations_text = smart_unicode(row[24], errors='ignore')
    account_text = smart_unicode(row[23], errors='ignore')
    range_text = smart_unicode(row[25], errors='ignore')

    program  = get_or_create_program(program_number.strip())
    program.title = program_title
    
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

    version = file_name[-9:-4]
    reader.next()
    for row in reader:
        parse_cfda_line(row, version)



