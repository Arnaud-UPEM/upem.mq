# Generated by Django 2.2.19 on 2021-07-26 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('education', '0002_delete_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant_de_l_etablissement', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('nom_etablissement', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('type_etablissement', models.CharField(blank=True, choices=[('DEFAUT', 'DEFAUT'), ('AUTRE', 'AUTRE'), ('Ecole', 'ECOLE'), ('Collège', 'COLLEGE'), ('Lycée', 'LYCEE'), ('SERVICE ADMINSTRATIF', 'ADMIN'), ('INFORMATION ET ORIENTATION', 'INFO')], default='DEFAUT', max_length=128, null=True)),
                ('status_public_prive', models.CharField(blank=True, choices=[('DEFAUT', 'DEFAUT'), ('AUTRE', 'AUTRE'), ('PUBLIC', 'PUBLIC'), ('PRIVE', 'PRIVE')], default='DEFAUT', max_length=128, null=True)),
                ('etat', models.CharField(blank=True, choices=[('DEFAUT', 'DEFAUT'), ('AUTRE', 'AUTRE'), ('OUVERT', 'OUVERT'), ('A FERMER', 'FERME')], default='DEFAUT', max_length=128, null=True)),
                ('ecole_maternelle', models.BooleanField(blank=True, default=False, null=True)),
                ('ecole_elementaire', models.BooleanField(blank=True, default=False, null=True)),
                ('voie_generale', models.BooleanField(blank=True, default=False, null=True)),
                ('voie_technologique', models.BooleanField(blank=True, default=False, null=True)),
                ('voie_professionnelle', models.BooleanField(blank=True, default=False, null=True)),
                ('fax', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('web', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('telephone', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('mail', models.EmailField(blank=True, default='', max_length=64, null=True)),
                ('adresse_1', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('adresse_2', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('adresse_3', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('code_postal', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('code_commune', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('nom_commune', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('restauration', models.BooleanField(blank=True, default=False, null=True)),
                ('hebergement', models.BooleanField(blank=True, default=False, null=True)),
                ('ulis', models.BooleanField(blank=True, default=False, null=True)),
                ('apprentissage', models.BooleanField(blank=True, default=False, null=True)),
                ('segpa', models.BooleanField(blank=True, default=False, null=True)),
                ('section_arts', models.BooleanField(blank=True, default=False, null=True)),
                ('section_cinema', models.BooleanField(blank=True, default=False, null=True)),
                ('section_theatre', models.BooleanField(blank=True, default=False, null=True)),
                ('section_sport', models.BooleanField(blank=True, default=False, null=True)),
                ('section_internationale', models.BooleanField(blank=True, default=False, null=True)),
                ('section_europeenne', models.BooleanField(blank=True, default=False, null=True)),
                ('lycee_agricole', models.BooleanField(blank=True, default=False, null=True)),
                ('lycee_militaire', models.BooleanField(blank=True, default=False, null=True)),
                ('lycee_des_metiers', models.BooleanField(blank=True, default=False, null=True)),
                ('post_bac', models.BooleanField(blank=True, default=False, null=True)),
                ('appartenance_education_prioritaire', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('siren_siret', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('fiche_onisep', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('nombre_d_eleves', models.IntegerField(blank=True, default=0, null=True)),
                ('date_ouverture', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('date_maj_ligne', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('type_contrat_prive', models.CharField(blank=True, choices=[('DEFAUT', 'DEFAUT'), ('AUTRE', 'AUTRE'), ('SANS OBJET', 'SANS_OBJET'), ('HORS CONTRAT', 'HORS_CONTRAT'), ("CONTRAT D'ASSOCIATION TOUTES CLASSES", 'CONTRAT_ASSO_TTS_CLASSES'), ('CONTRAT ASSOCIATION PARTIES DES CLASSES', 'CONTRAT_ASSO_PART_CLASSES'), ('CONTRAT SIMPLE TOUTES CLASSES', 'CONTRAT_SIMPLE_TTS_CLASSES'), ('CONTRAT SIMPLE PARTIE DES CLASSES', 'CONTRAT_SIMPLE_PART_CLASSES')], default='DEFAUT', max_length=64, null=True)),
            ],
        ),
    ]
