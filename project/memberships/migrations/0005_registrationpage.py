# Generated by Django 2.2.19 on 2021-07-10 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0060_fix_workflow_unique_constraint'),
        ('memberships', '0004_delete_registrationpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('seo_keywords', models.CharField(blank=True, help_text="Optional. 'Search Engine Friendly' keywords. This will appear in head metadata.", max_length=255, verbose_name='page keywords')),
                ('seo_description', models.CharField(blank=True, help_text="Optional. 'Search Engine Friendly' description. This will appear in head metadata.", max_length=255, verbose_name='page description')),
                ('template_credentials', models.CharField(default='memberships/credentials_page.html', max_length=125)),
                ('template_memberships', models.CharField(default='memberships/memberships_page.html', max_length=125)),
            ],
            options={
                'verbose_name': 'Memberships: Inscription',
            },
            bases=('wagtailcore.page',),
        ),
    ]
