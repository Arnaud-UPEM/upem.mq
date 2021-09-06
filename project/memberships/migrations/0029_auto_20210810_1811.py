# Generated by Django 2.2.19 on 2021-08-10 18:11

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0028_auto_20210810_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributionplan',
            name='contribution',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='memberships.Contribution'),
        ),
    ]
