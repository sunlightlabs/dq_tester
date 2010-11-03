from cfda.models import *
import csv
from settings import PROJECT_ROOT
def find_nonreporters():
   
    writer = csv.writer(open("%s/data/nonreporting_programs_2007_2010.csv" % PROJECT_ROOT, 'w')) 
    writer.writerow(("Program Number", "Program Title", "Fiscal Year", "CFDA Obligation", "USASpending Obligation Total"))
    nr = Program.objects.filter(obligations__exists=True, obligations__usaspending_amount__exists=False)
    for p in nr:
        for o in p.obligations:
            if o.fiscal_year < 2011 and (not o.usaspending_amount or o.usaspending_amount == 0) and o.amount > 0:
                writer.writerow((p.number, p.title, o.fiscal_year, o.amount, o.usaspending_amount or 0))

if __name__ == "__main__":
    find_nonreporters()
