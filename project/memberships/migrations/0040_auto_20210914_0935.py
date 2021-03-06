# Generated by Django 2.2.19 on 2021-09-14 13:35

import datetime
from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0039_auto_20210910_2224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='memberapplication',
            name='date_signed',
        ),
        migrations.AlterField(
            model_name='application',
            name='condition',
            field=wagtail.core.fields.RichTextField(blank=True, verbose_name='Condition de candidature'),
        ),
        migrations.CreateModel(
            name='MemberApplicationChild',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_signed', models.DateTimeField(default=datetime.datetime.now, verbose_name='Date accord')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_application', to='memberships.Application')),
                ('member_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_applications', to='memberships.MemberApplication')),
            ],
            options={
                'verbose_name': 'Membre: Candidature par Ecole',
            },
        ),
    ]
