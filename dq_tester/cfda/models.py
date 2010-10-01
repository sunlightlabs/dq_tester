from mongoengine import connect, Document, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, ListField, DictField
from settings import DATABASE_NAME

connect(DATABASE_NAME)

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


class FundingType(EmbeddedDocument):
    code = IntField(required=True)
    name = StringField()

class Obligation(EmbeddedDocument):
    fiscal_year = IntField(required=True)
    amount = IntField()
    funding_type = FundingType()

class AssistanceType(EmbeddedDocument):
    number = IntField(required=True)
    name = StringField()

class Program(Document):
    _id = StringField(required=True, max_length=6)
    description = StringField()
    funding_types = ListField(EmbeddedDocumentField(FundingType))
    obligations = ListField(EmbeddedDocumentField(Obligation))
    assistance_types = ListField(EmbeddedDocumentField(AssistanceType))
    average_assist = IntField()
    range_assist = ListField(IntField())
    run = StringField()

