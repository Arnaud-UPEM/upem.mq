import enum
import json
from datetime import datetime
from django.core.management.base import BaseCommand

from user.models import Auth
from memberships.models import Application


class Command (BaseCommand):
    help_text = 'Seed Application (Candidature)'

    def seed_applications (self):
        Application.objects.all().delete()

        c1 = Application.objects.create(
            id=1,
            name='Candidature 2021 - 2022',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2021, 9, 1),
            date_end=datetime(2022, 8, 31),
            is_active=True
        )

        c2 = Application.objects.create(
            id=2,
            name='Candidature 2020 - 2021',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2020, 9, 1),
            date_end=datetime(2021, 8, 31),
            is_active=False
        )

        c3 = Application.objects.create(
            id=3,
            name='Candidature 2019 - 2020',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2019, 9, 1),
            date_end=datetime(2020, 8, 31),
            is_active=False
        )

        c4 = Application.objects.create(
            id=4,
            name='Candidature 2018 - 2019',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2018, 9, 1),
            date_end=datetime(2019, 8, 31),
            is_active=False
        )

        # self.member1.contributions.create(
        #     price=20.0,
        #     contribution=Contribution.objects.get(pk=1)
        # )
        # self.member1.contributions.create(
        #     price=20.0,
        #     contribution=Contribution.objects.get(pk=2)
        # )
        # self.member1.contributions.create(
        #     price=20.0,
        #     contribution=Contribution.objects.get(pk=3)
        # )

        # self.member2.contributions.create(
        #     price=10.0,
        #     contribution=Contribution.objects.get(pk=1)
        # )
        # self.member2.contributions.create(
        #     price=10.0,
        #     contribution=Contribution.objects.get(pk=2)
        # )
        # self.member2.contributions.create(
        #     price=10.0,
        #     contribution=Contribution.objects.get(pk=4)
        # )


    def handle (self, *args, **kwargs):
        self.seed_applications ()