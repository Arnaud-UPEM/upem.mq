# Generated by Django 2.2.19 on 2021-08-03 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        ('user', '0007_logoutpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnauthorizedPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Auth: Accès non autorisé',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterModelOptions(
            name='loginlandingpage',
            options={'verbose_name': 'Auth: Connexion - Landing Test'},
        ),
        migrations.AlterModelOptions(
            name='loginpage',
            options={'verbose_name': 'Auth: Connexion'},
        ),
    ]
