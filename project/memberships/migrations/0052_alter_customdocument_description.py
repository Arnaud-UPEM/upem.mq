# Generated by Django 3.2.7 on 2021-09-21 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0051_customdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customdocument',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Description'),
        ),
    ]
