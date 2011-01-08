
from django.core.management.base import BaseCommand
from tests.year_over_year import year_over_year
from tests.under_minimum import under_minimum
from tests.under_maximum import under_maximum
from pymongo import Connection
from django.conf import settings

class Command(BaseCommand):
    args = 'none'
    help = 'runs various tests on all loaded CFDA programs'

    def handle(self, *args, **options):
        conn = Connection()
        db = conn[settings.DATABASE_NAME]
        year_over_year(db)
        under_minimum(db)
        under_maximum(db)
