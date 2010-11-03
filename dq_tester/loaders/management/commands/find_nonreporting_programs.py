
from django.core.management.base import BaseCommand
from loaders.find_nonreporting_programs import find_nonreporters

class Command(BaseCommand):
    args = 'none'
    help = 'writes nonreporting programs to a csv file'

    def handle(self, *args, **options):
        find_nonreporters()


