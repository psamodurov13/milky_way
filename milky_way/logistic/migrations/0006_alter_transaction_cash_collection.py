# Generated by Django 4.2.6 on 2023-10-19 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0005_alter_parcel_delivered_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='cash_collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='logistic.cashcollection', verbose_name='Инкассация'),
        ),
    ]