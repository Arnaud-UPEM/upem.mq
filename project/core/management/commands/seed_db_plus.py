import enum
import json
from random import randint
from datetime import datetime
from django.core.management.base import BaseCommand

from education.models import School
from memberships.models import Application, MemberApplication, Contribution, ContributionPlan, Member, MemberChild, MemberContribution
from user.models import Auth


class Command (BaseCommand):
    help_text = ''

    def _get_name (self):
        return self.names[
            randint (0, len(self.names) - 1)
        ]
    
    def _create_parent (self, app):
        name = self._get_name()

        while Member.objects.filter(first_name=name):
            name = self._get_name()   

        auth = Auth.objects.create(
            email=f'parent_{name}@mail.fr',
        )
        auth.set_password('password')
        auth.save()

        member = Member.objects.create(
            auth=auth,
            last_name='PARENT',
            first_name=name,
            job='Tester',
        )

        for id in range (1, 5):
            if randint (0, 1):
                member.contributions.create(
                    price=20.0,
                    contribution=Contribution.objects.get(pk=id)
                )

        for i in range (0, 5):
            child = self._create_child (member)
            
            if randint (0, 1):
                member.applications.create(
                    child=child,
                    application=app,
                )

        return member

    def _create_child (self, member):
        name = self._get_name()

        while MemberChild.objects.filter(member=member, first_name=name):
            name = self._get_name()

        school = School.objects.get(pk=randint(961, 985))

        return member.children.create(
            dob=datetime.now(),
            school=school,
            last_name='ENFANT',
            first_name=name,
        )

    '''
    Clean
        Application, Contribution, and members tickets
    Create
        Applicaiton and Contribution
    '''
    def seed_contributions (self):
        Application.objects.all().delete()
        Contribution.objects.all().delete()
        ContributionPlan.objects.all().delete()
        MemberApplication.objects.all().delete()
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

        a1 = Application.objects.create(
            id=1,
            name='Candidature 2021 - 2022',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            condition='<h2 data-block-key="a7bwz">Lorem ipsum dolor sit amet,</h2><p data-block-key="g1o3l">consectetur adipiscing elit. Morbi elementum lorem sed maximus luctus. Phasellus bibendum semper condimentum. Mauris eget cursus purus, ac posuere quam. Maecenas venenatis et sapien sit amet dictum. Praesent nibh lacus, posuere sed consectetur vitae, eleifend eget odio. Donec suscipit urna nec neque vulputate interdum.</p>',
            date_start=datetime(2021, 9, 1),
            date_end=datetime(2022, 8, 31),
            is_active=True
        )

        a2 = Application.objects.create(
            id=2,
            name='Candidature 2020 - 2021',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            condition='<h2 data-block-key="a7bwz">Lorem ipsum dolor sit amet,</h2><p data-block-key="g1o3l">consectetur adipiscing elit. Morbi elementum lorem sed maximus luctus. Phasellus bibendum semper condimentum. Mauris eget cursus purus, ac posuere quam. Maecenas venenatis et sapien sit amet dictum. Praesent nibh lacus, posuere sed consectetur vitae, eleifend eget odio. Donec suscipit urna nec neque vulputate interdum.</p>',
            date_start=datetime(2020, 9, 1),
            date_end=datetime(2021, 8, 31),
            is_active=False
        )

        a3 = Application.objects.create(
            id=3,
            name='Candidature 2019 - 2020',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            condition='<h2 data-block-key="a7bwz">Lorem ipsum dolor sit amet,</h2><p data-block-key="g1o3l">consectetur adipiscing elit. Morbi elementum lorem sed maximus luctus. Phasellus bibendum semper condimentum. Mauris eget cursus purus, ac posuere quam. Maecenas venenatis et sapien sit amet dictum. Praesent nibh lacus, posuere sed consectetur vitae, eleifend eget odio. Donec suscipit urna nec neque vulputate interdum.</p>',
            date_start=datetime(2019, 9, 1),
            date_end=datetime(2020, 8, 31),
            is_active=False
        )

        a4 = Application.objects.create(
            id=4,
            name='Candidature 2018 - 2019',
            description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            condition='<h2 data-block-key="a7bwz">Lorem ipsum dolor sit amet,</h2><p data-block-key="g1o3l">consectetur adipiscing elit. Morbi elementum lorem sed maximus luctus. Phasellus bibendum semper condimentum. Mauris eget cursus purus, ac posuere quam. Maecenas venenatis et sapien sit amet dictum. Praesent nibh lacus, posuere sed consectetur vitae, eleifend eget odio. Donec suscipit urna nec neque vulputate interdum.</p>',
            date_start=datetime(2018, 9, 1),
            date_end=datetime(2019, 8, 31),
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

    def seed_members (self):
        Auth.objects.filter(id__gt=1).delete()
        Member.objects.all().delete()
        MemberChild.objects.all().delete

        app = Application.objects.get(is_active=True)

        for i in range (0, 50):
            self._create_parent (app)

    def handle (self, *args, **kwargs):
        self.seed_contributions()
        self.seed_members()

    names = [
        'Phebe',
        'Welch',
        'Helin',
        'Pennington',
        'Gemma',
        'Bright',
        'Latoya',
        'Bevan',
        'Vanessa',
        'Fenton',
        'Aditya',
        'Weiss',
        'Usama',
        'Mata',
        'Mary',
        'Tran',
        'Yahya',
        'Foreman',
        'Amiyah',
        'Barnard',
        'Hoorain',
        'Tomlinson',
        'Susannah',
        'Stephenson',
        'Ajay',
        'French',
        'Wilson',
        'Woodley',
        'Elaina',
        'Forbes',
        'Milan',
        'Parks',
        'Neha',
        'Padilla',
        'Tallulah',
        'Emerson',
        'Saira',
        'Hardin',
        'Carolina',
        'Steadman',
        'Darcie-Mae',
        'Thatcher',
        'Presley',
        'Hines',
        'Kasper',
        'Mathis',
        'Jermaine',
        'Castillo',
        'Evie-Grace',
        'Kavanagh',
        'Trystan',
        'Welsh',
        'Remi',
        'Zavala',
        'Amanda',
        'Harding',
        'Kristie',
        'Villalobos',
        'Anabella',
        'Little',
        'Joel',
        'Bell',
        'Sophie-Louise',
        'Ware',
        'Dion',
        'Avila',
        'Joely',
        'Pritchard',
        'Jay',
        'Scott',
        'Tadhg',
        'Mcgowan',
        'Karolina',
        'Ewing',
        'Nico',
        'Hanna',
        'Miguel',
        'Leal',
        'Naeem',
        'Esquivel',
        'Teodor',
        'Leonard',
        'Arthur',
        'Dalby',
        'Ewen',
        'Senior',
        'Alec',
        'Davey',
        'Kade',
        'Bender',
        'Dawn',
        'Neville',
        'Samir',
        'Weber',
        'Dahlia',
        'Rees',
        'Gia',
        'Cairns',
        'Keanan',
        'Nicholls',
    ]