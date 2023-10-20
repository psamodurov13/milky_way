from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from milky_way.settings import logger
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .utils import get_balance


from .models import Parcel, Customer, Office, Payer, CashCollection
from users.models import User


def custom_phone_validator(value):
    logger.info(f'VALUE - {value}')
    logger.info(f'VALIDATION - {value.is_valid()}')
    if not value.is_valid():
        raise ValidationError("Введен не корректный номер телефона (RU)")

def custom_name_validator(value):
    if type(value) != str:
        raise ValidationError("ФИО должны состоять из букв")
    if len(str(value)) < 3:
        raise ValidationError("Значение поля должно состоять минимум из 3 букв")


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class NewParcelForm(forms.Form):
    from_customer = forms.CharField(label='Отправитель', widget=forms.TextInput())
    from_customer_phone = PhoneNumberField(label='Телефон отправителя', widget=forms.TextInput())
    to_customer = forms.CharField(label='Получатель', widget=forms.TextInput())
    to_customer_phone = PhoneNumberField(label='Телефон получателя', widget=forms.TextInput())
    payer = forms.ChoiceField(label='Плательщик', choices=[(i.id, i.name) for i in Payer.objects.all()],
                              widget=forms.RadioSelect())
    price = forms.FloatField(label='Стоимость')
    payment_status = forms.BooleanField(label='Оплачен', widget=forms.CheckboxInput(), required=False)


class SearchParcelsForm(forms.Form):
    search = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Поиск'}), required=False)


class CashCollectionForm(forms.ModelForm):
    class Meta:
        model = CashCollection
        fields = ['amount', 'office']

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        current_balance = get_balance(cleaned_data.get('office'))
        logger.info(f'AMOUNT - {amount}, CURRENT AMOUNT - {current_balance}')

        errors = {}
        if amount > current_balance:
            errors['amount'] = ValidationError(f"Сумма не может быть больше текущей суммы в кассе ({current_balance})")
        if errors:
            raise ValidationError(errors)