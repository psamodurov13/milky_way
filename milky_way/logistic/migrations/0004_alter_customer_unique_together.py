# Generated by Django 4.2.6 on 2023-10-19 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0003_parcel_from_office_parcel_to_office'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together={('name', 'phone')},
        ),
    ]
