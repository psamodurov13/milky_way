# Generated by Django 4.2.6 on 2023-10-16 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='logistic.office', verbose_name='Офис'),
        ),
    ]
