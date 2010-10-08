from mongoengine import connect, Document, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, ListField, DictField, ObjectIdField
from settings import DATABASE_NAME
import re
connect(DATABASE_NAME)


ASSIST_OPTIONS = (
        (1, "Formula Grants", re.compile('formula.*grants')),
        (2, "Project Grants", re.compile('project.*grants|loans\/grants')),
        (3, "Direct Payments for Specified Use", re.compile('direct.*payments.*specified')),
        (4, "Direct Payments with Unrestricted Use", re.compile('direct.*payments.*unrestricted')),
        (5, "Direct Loans", re.compile('direct.*loans')),
        (6, "Guaranteed/Insured Loans", re.compile('guaran.*loan|loan.*guaran')),
        (7, "Insurance", re.compile('insur.*')),
        (8, "Sale, Exchange, or Donation of Property and Goods", re.compile('sale.*exchange')),
        (9, "Use of Property, Facilities, and Equipment", re.compile('property.*facilit')),
        (10, "Provision of Specialized Services", re.compile('specialized.*')),
        (11, "Advisory Services and Counseling", re.compile('advis.*counsel')),
        (12, "Dissemination of Technical Information", re.compile('dissem.*tech|information')),
        (13, "Training", re.compile('training')),
        (14, "Investigation of Complaints", re.compile('investigation')),
        (15, "Federal Employment", re.compile('employment')),
        (16, "Cooperative Agreements", re.compile('coop.*agree')),
    )



class BudgetNumber(EmbeddedDocument):
    fiscal_year = IntField(required=True)
    amount = IntField()

class BudgetAccount(EmbeddedDocument):
    code = StringField()
    fund_code = IntField()
    subfunction_code = IntField()
    transmittal_code = IntField()
    account_symbol = IntField()
    

class Subagency(EmbeddedDocument):
    name = StringField()
    cfda_code = IntField()
    treasury_code = IntField()
    budget_numbers = ListField(EmbeddedDocumentField(BudgetNumber))
    outlays = ListField(DictField())

class Agency(EmbeddedDocument):
    cfda_code = IntField()
    treasury_code = IntField()
    subagency = ListField(EmbeddedDocumentField(Subagency))
    name = StringField()
    budget_numbers = ListField(EmbeddedDocumentField(BudgetNumber))

class Obligation(EmbeddedDocument):
    fiscal_year = IntField(required=True)
    amount = IntField()
    assistance_type = IntField()

class Program(Document):
    number = StringField(required=True, unique=True)
    title = StringField()
    description = StringField()
    obligations = ListField(EmbeddedDocumentField(Obligation))
    assistance_types = ListField(IntField())
    average_assist = IntField()
    range_assist = ListField(IntField())
    run = StringField()
    
  
