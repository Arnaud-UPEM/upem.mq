# Generated by Django 2.2.19 on 2021-09-14 14:28

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0041_auto_20210914_1019'),
    ]

    operations = [
        migrations.RenameField(
            model_name='memberapplicationorderable',
            old_name='member_application_child',
            new_name='application_child',
        ),
        migrations.AddField(
            model_name='memberapplicationorderable',
            name='application',
            field=modelcluster.fields.ParentalKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='application_lists', to='memberships.MemberApplication'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='memberapplication',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members_application', to='memberships.Application', verbose_name='Candidature'),
        ),
    ]
