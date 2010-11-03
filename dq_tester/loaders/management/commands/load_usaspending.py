
from django.core.management.base import BaseCommand
from loaders.usaspending_loader import load_usaspending

class Command(BaseCommand):
    args = 'none'
    help = 'imports usaspending data for CFDA programs'

    def handle(self, *args, **options):
        load_usaspending()

