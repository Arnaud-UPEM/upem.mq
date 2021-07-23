from django.core.management.base import BaseCommand, CommandError

from .forms import SchoolForm
from .models import School

class Command(BaseCommand):
    help = 'Remove all rows and seed with new ones'

    def core (self.)

    def handle(self, *args, **options):
        with f as open('fr-en-annuaire-education.json', 'r'):
            pass