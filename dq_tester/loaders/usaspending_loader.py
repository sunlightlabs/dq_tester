import MySQLdb
from cfda.models import *
from mongoengine.queryset import DoesNotExist
import csv
from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT, MYSQL_TABLE_NAME

def load_usaspending():
    MIN_FY = 2006  # We only want fiscal years over 2006
    conn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE, port=MYSQL_PORT)
    cursor = conn.cursor()

    programs = Program.objects.order_by('program_number')
    program_data = {}

    usa_query = "SELECT cfda_program_num, fiscal_year, SUM(fed_funding_amount), SUM(face_loan_guran) FROM %s WHERE fiscal_year > %s GROUP BY cfda_program_num, fiscal_year ORDER BY cfda_program_num" % (MYSQL_TABLE_NAME, MIN_FY)
    print usa_query
    print "fetching summary query with rollup of programs, fiscal years and total obligations"
    cursor.execute(usa_query)

    rows = cursor.fetchall()
    
    for row in rows:
        try:    
            program = Program.objects.get(number=row[0])
            if program.obligations:
                for cfda_ob in program.obligations:
                    if cfda_ob['fiscal_year'] == int(row[1]):
                        if cfda_ob.assistance_type in [1, 2, 3, 4]:
                            #its direct spending/grants
                            obligation = row[2]
                        else:
                            #it's a loan/guarantee, or insurance
                            obligation = row[3]
                    
                        cfda_ob.usaspending_amount = obligation
                        cfda_ob.delta = (cfda_ob.usaspending_amount - cfda_ob.amount)
                        try:
                            cfda_ob.weighted_delta = float(cfda_ob.delta / cfda_ob.amount)
                        except Exception:
                            if cfda_ob.amount == 0:
                                if not cfda_ob.usaspending_amount:
                                    cfda_ob.weighted_delta = 0.0
                                else:
                                    cfda_ob.weighted_delta = None
                        program.save()

                    #print "MATCH: %s - %s - %s - %s diff %s" % (row[0], row[1], cfda_ob.obligation, cfda_ob.usaspending_obligation, cfda_ob.delta)

        except DoesNotExist, e:
            print row[0]

    cursor.close()
    conn.close()


if __name__== "__main__":

    load_usaspending()
