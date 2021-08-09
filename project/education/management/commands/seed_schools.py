import json

from django.core.management.base import BaseCommand, CommandError

from education.forms import SchoolForm
from education.models import School, EtatEnum, StatusEnum, TypeEtabEnum

class Command(BaseCommand):
    help = 'Remove all rows and seed with new ones'

    def base_school (self):
        School.objects.create(
            id=1,
            nom_etablissement='AUTRE',
            identifiant_de_l_etablissement='0',
            etat=EtatEnum.AUTRE,
            type_etablissement=TypeEtabEnum.AUTRE,
            status_public_prive=StatusEnum.AUTRE
        )

    def row (self, fields):
        # Data cleaning
        # if 'type_contrat_prive' in fields:
        #     fields['type_contrat_prive'].replace('\'', '')
        #     fields['type_contrat_prive'].replace(' ', '_')
        #     pass

        f = SchoolForm(fields)
        if f.is_valid():
            f.save()

        else:
            print (f.errors)

    def handle(self, *args, **options):
        School.objects.all().delete()

        self.base_school()

        with open('project/education/management/commands/fr-en-annuaire-education.json', 'r') as f:
            raw = f.readline().encode('utf-8')
            data = json.loads(raw)
            
            print (len(data))

            for x in data:
                self.row (x['fields'])




