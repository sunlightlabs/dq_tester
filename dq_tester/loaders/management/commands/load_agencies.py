from django.core.management.base import BaseCommand
from loaders.agency_loader import load_agencies

class Command(BaseCommand):
    args = 'none'
    help = 'imports agencies'

    def handle(self, *args, **options):
        load_agencies()


