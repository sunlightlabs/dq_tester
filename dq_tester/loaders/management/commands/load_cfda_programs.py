from django.core.management.base import BaseCommand
from loaders.cfda_loader import load_cfda

class Command(BaseCommand):
    args = 'cfda_file_name.csv'
    help = 'imports CFDA programs and related obligatons, budgets accounts, and agencies'

    def handle(self, *args, **options):
        for file_name in args:
            load_cfda(file_name)

        
