from django.db import models
from milky_way.utils import CustomStr
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
User = get_user_model()


class City(CustomStr, models.Model):
    name = models.CharField(verbose_name='Название города', max_length=255)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Office(CustomStr, models.Model):
    name = models.CharField(verbose_name='Название офиса', max_length=255)
    city = models.ForeignKey(City, verbose_name='Город', on_delete=models.CASCADE, related_name='offices')
    address = models.CharField(verbose_name='Адрес', max_length=255)

    class Meta:
        verbose_name = 'Офис'
        verbose_name_plural = 'Офисы'


class Payer(CustomStr, models.Model):
    name = models.CharField(verbose_name='Название типа плательщика', max_length=255)

    class Meta:
        verbose_name = 'Плательщик'
        verbose_name_plural = 'Плательщики'


class Customer(CustomStr, models.Model):
    name = models.CharField(verbose_name='Фамилия Имя Отчество')
    phone = PhoneNumberField(verbose_name='Телефон')
    email = models.EmailField(verbose_name='e-mail', blank=True)
    telegram = models.CharField(verbose_name='Telegram', max_length=255, blank=True,
                                help_text='В поле указывается username аккаунта (не ID и не телефон)')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class CashCollection(CustomStr, models.Model):
    date_time = models.DateTimeField(verbose_name='Дата инкассации', auto_now_add=True)
    office = models.ForeignKey(Office, verbose_name='Офис', related_name='cash_collections', on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Сумма инкассации')

    class Meta:
        verbose_name = 'Инкассация'
        verbose_name_plural = 'Инкассации'


class ShipStatus(CustomStr, models.Model):
    name = models.CharField(max_length=100, verbose_name='Название статуса посылки')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class Parcel(CustomStr, models.Model):
    from_office = models.ForeignKey(Office, verbose_name='Пункт отправления', on_delete=models.CASCADE,
                                    related_name='parcels_from_office')
    from_customer = models.ForeignKey(Customer, verbose_name='Отправитель', on_delete=models.CASCADE,
                                      related_name='parcels_from')
    to_office = models.ForeignKey(Office, verbose_name='Пункт доставки', on_delete=models.CASCADE,
                                  related_name='parcels_to_office')
    to_customer = models.ForeignKey(Customer, verbose_name='Получатель', on_delete=models.CASCADE,
                                    related_name='parcels_to')
    created_at = models.DateTimeField(verbose_name='Дата и время отправки', auto_now_add=True)
    payer = models.ForeignKey(Payer, verbose_name='Плательщик', on_delete=models.CASCADE, related_name='parcels')
    payment_status = models.BooleanField(default=False, verbose_name='Оплачен')
    ship_status = models.ForeignKey(ShipStatus, verbose_name='Статус посылки', on_delete=models.CASCADE,
                                    related_name='parcels')
    price = models.FloatField(verbose_name='Стоимость доставки')
    created_by = models.ForeignKey(User, verbose_name='Принял посылку', on_delete=models.PROTECT,
                                   related_name='parcels_created')
    delivered_by = models.ForeignKey(User, verbose_name='Выдал посылку', on_delete=models.PROTECT,
                                     related_name='parcels_delivered')
    complete_date = models.DateTimeField(verbose_name='Дата вручения', blank=True, null=True)

    class Meta:
        verbose_name = 'Посылка'
        verbose_name_plural = 'Посылки'


class Transaction(CustomStr, models.Model):
    parcel = models.ForeignKey(Parcel, verbose_name='Посылка', on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField(verbose_name='Полученная сумма')
    office = models.ForeignKey(Office, verbose_name='Офис', on_delete=models.CASCADE, related_name='transactions')
    date_time = models.DateTimeField(verbose_name='Дата и время оплаты')
    cash_collected = models.BooleanField(default=False, verbose_name='Инкассация произведена')
    cash_collection = models.ForeignKey(CashCollection, verbose_name='Инкассация', on_delete=models.CASCADE,
                                        related_name='transactions')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'




