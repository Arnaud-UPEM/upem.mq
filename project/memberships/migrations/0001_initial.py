# Generated by Django 2.2.19 on 2021-07-06 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(default='', max_length=100, verbose_name='Nom')),
                ('first_name', models.CharField(default='', max_length=100, verbose_name='Prénom')),
                ('email', models.EmailField(default='', max_length=254, verbose_name='Email')),
                ('city', models.CharField(default='', max_length=60, verbose_name='Ville')),
                ('country', models.CharField(default='', max_length=60, verbose_name='Pays')),
                ('address1', models.CharField(default='', max_length=100, verbose_name='Ligne 1')),
                ('address2', models.CharField(default='', max_length=100, verbose_name='Ligne 2')),
                ('zip_code', models.CharField(default='', max_length=60, verbose_name='Code Postal')),
                ('job', models.CharField(default='', max_length=60, verbose_name='Profession')),
                ('phone_pro', models.CharField(default='', max_length=60, verbose_name='Téléphone professionnel')),
                ('phone_cell', models.CharField(default='', max_length=60, verbose_name='Téléphone mobile')),
                ('phone_home', models.CharField(default='', max_length=60, verbose_name='Téléphone fixe')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_end', models.DateField(verbose_name='Date fin')),
                ('date_start', models.DateField(verbose_name='Date début')),
                ('is_active', models.BooleanField(default=False, verbose_name='Active ?')),
            ],
        ),
        migrations.CreateModel(
            name='MemberChild',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(default='', max_length=100, verbose_name='Nom')),
                ('first_name', models.CharField(default='', max_length=100, verbose_name='Prénom')),
                ('grade', models.CharField(default='', max_length=20, verbose_name='Classe')),
                ('school', models.CharField(default='', max_length=100, verbose_name='Etablissement')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='memberships.Member')),
            ],
        ),
    ]
