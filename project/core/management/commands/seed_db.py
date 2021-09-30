import enum
import json
from datetime import datetime
from django.core.management.base import BaseCommand

from user.models import Auth
from memberships.models import Contribution, ContributionPlan, Member, MemberChild, MemberContribution


class Command (BaseCommand):
    help_text = ''

    def seed_auth (self):
        Auth.objects.filter(id__gt=1).delete()
        Member.objects.all().delete()

        auth1 = Auth.objects.create(
            id=2,
            email='test1@mail.fr',
        )
        auth1.set_password('password1')
        auth1.save()

        auth2 = Auth.objects.create(
            id=3,
            email='test2@mail.fr',
        )
        auth2.set_password('password2')
        auth2.save()

        self.member1 = Member.objects.create(
            id=2,
            auth=auth1,
            last_name='TEST',
            first_name='Member 1',
            job='Tester',
        )

        self.member2 = Member.objects.create(
            id=3,
            auth=auth2,
            last_name='TEST',
            first_name='Member 2',
            job='Tester',
        )

    def seed_contributions (self):
        Contribution.objects.all().delete()
        ContributionPlan.objects.all().delete()
        MemberContribution.objects.all().delete()

        c1 = Contribution.objects.create(
            id=1,
            name='Cotisation 2021 - 2022',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2021, 9, 1),
            date_end=datetime(2022, 8, 31),
            base_price=20.0,
            is_active=True
        )

        c2 = Contribution.objects.create(
            id=2,
            name='Cotisation 2020 - 2021',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2020, 9, 1),
            date_end=datetime(2021, 8, 31),
            base_price=20.0,
            is_active=False
        )

        c3 = Contribution.objects.create(
            id=3,
            name='Cotisation 2019 - 2020',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2019, 9, 1),
            date_end=datetime(2020, 8, 31),
            base_price=20.0,
            is_active=False
        )

        c4 = Contribution.objects.create(
            id=4,
            name='Cotisation 2018 - 2019',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            date_start=datetime(2018, 9, 1),
            date_end=datetime(2019, 8, 31),
            base_price=20.0,
            is_active=False
        )

        """
        Remove ContributionPlan references

        id = 1
        for c in [c1, c2, c3, c4]:
            ContributionPlan.objects.create(
                id=id,
                name='Tarif de base',
                mod=0.0,
                contribution=c
            )
            ContributionPlan.objects.create(
                id=id+1,
                name='Tarif Prémium',
                mod=20.0,
                contribution=c
            )
            ContributionPlan.objects.create(
                id=id+2,
                name='Tarif Prémium +',
                mod=30.0,
                contribution=c
            )
            id += 3
        """

        self.member1.contributions.create(
            price=20.0,
            contribution=Contribution.objects.get(pk=1)
        )
        # self.member1.contributions.create(
        #     price=20.0,
        #     contribution=Contribution.objects.get(pk=2)
        # )
        self.member1.contributions.create(
            price=20.0,
            contribution=Contribution.objects.get(pk=3)
        )

        self.member2.contributions.create(
            price=10.0,
            contribution=Contribution.objects.get(pk=1)
        )
        self.member2.contributions.create(
            price=10.0,
            contribution=Contribution.objects.get(pk=2)
        )
        # self.member2.contributions.create(
        #     price=10.0,
        #     contribution=Contribution.objects.get(pk=4)
        # )


    def handle (self, *args, **kwargs):
        self.seed_auth()
        self.seed_contributions()