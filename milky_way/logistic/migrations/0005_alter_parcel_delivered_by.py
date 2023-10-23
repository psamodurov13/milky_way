# Generated by Django 4.2.6 on 2023-10-19 06:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logistic', '0004_alter_customer_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='delivered_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parcels_delivered', to=settings.AUTH_USER_MODEL, verbose_name='Выдал посылку'),
        ),
    ]