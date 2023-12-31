# Generated by Django 4.2.6 on 2023-10-16 06:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import milky_way.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logistic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True, verbose_name='Дата инкассации')),
                ('amount', models.IntegerField(verbose_name='Сумма инкассации')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_collections', to='logistic.office', verbose_name='Офис')),
            ],
            options={
                'verbose_name': 'Инкассация',
                'verbose_name_plural': 'Инкассации',
            },
            bases=(milky_way.utils.CustomStr, models.Model),
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время отправки')),
                ('payment_status', models.BooleanField(default=False, verbose_name='Оплачен')),
                ('price', models.FloatField(verbose_name='Стоимость доставки')),
                ('complete_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата вручения')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parcels_created', to=settings.AUTH_USER_MODEL, verbose_name='Принял посылку')),
                ('delivered_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parcels_delivered', to=settings.AUTH_USER_MODEL, verbose_name='Выдал посылку')),
                ('from_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels_from', to='logistic.customer', verbose_name='Отправитель')),
                ('payer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels', to='logistic.payer', verbose_name='Плательщик')),
            ],
            options={
                'verbose_name': 'Посылка',
                'verbose_name_plural': 'Посылки',
            },
            bases=(milky_way.utils.CustomStr, models.Model),
        ),
        migrations.CreateModel(
            name='ShipStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название статуса посылки')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
            },
            bases=(milky_way.utils.CustomStr, models.Model),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Полученная сумма')),
                ('date_time', models.DateTimeField(verbose_name='Дата и время оплаты')),
                ('cash_collected', models.BooleanField(default=False, verbose_name='Инкассация произведена')),
                ('cash_collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='logistic.cashcollection', verbose_name='Инкассация')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='logistic.office', verbose_name='Офис')),
                ('parcel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='logistic.parcel', verbose_name='Посылка')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
            },
            bases=(milky_way.utils.CustomStr, models.Model),
        ),
        migrations.AddField(
            model_name='parcel',
            name='ship_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels', to='logistic.shipstatus', verbose_name='Статус посылки'),
        ),
        migrations.AddField(
            model_name='parcel',
            name='to_customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parcels_to', to='logistic.customer', verbose_name='Получатель'),
        ),
    ]
