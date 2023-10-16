from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


class User(AbstractUser):
    phone = PhoneNumberField(verbose_name='Телефон')
    office = models.ForeignKey('logistic.Office', verbose_name='Офис', on_delete=models.CASCADE, related_name='users', blank=True,
                               null=True)
    status = models.BooleanField(verbose_name='Статус', default=True)
