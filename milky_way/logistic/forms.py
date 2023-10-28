from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from milky_way.settings import logger
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .utils import get_balance, get_all_routes
import sys
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from .models import Parcel, Customer, Office, Payer, CashCollection, City
from users.models import User

if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    migrations = False
else:
    migrations = True


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
    if not migrations:
        to_office = forms.ChoiceField(label='Офис', choices=[(i.id, i.name) for i in Office.objects.all()],
                                      widget=forms.Select())
    to_customer = forms.CharField(label='Получатель', widget=forms.TextInput())
    to_customer_phone = PhoneNumberField(label='Телефон получателя', widget=forms.TextInput())
    if not migrations:
        payer = forms.ChoiceField(label='Плательщик', choices=[(i.id, i.name) for i in Payer.objects.all()],
                                  widget=forms.RadioSelect())
    price = forms.FloatField(label='Стоимость')

    def __init__(self, *args, **kwargs):
        to_city_id = kwargs.pop('to_city', None)
        super().__init__(*args, **kwargs)
        if not migrations and to_city_id:
            offices = [(i.id, i.name) for i in Office.objects.filter(city=City.objects.get(id=to_city_id))]
            self.fields['to_office'].choices = offices
        self.fields['from_customer_phone'].widget.attrs['data-phone-pattern'] = "+7 (___) ___-__-__"
        self.fields['from_customer_phone'].widget.attrs['placeholder'] = "+7 (___) ___-__-__"
        self.fields['to_customer_phone'].widget.attrs['data-phone-pattern'] = "+7 (___) ___-__-__"
        self.fields['to_customer_phone'].widget.attrs['placeholder'] = "+7 (___) ___-__-__"


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


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(label='От', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    end_date = forms.DateField(label='До', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    if not migrations:
        choices = [(f'{i["from_city"].id}-{i["to_city"].id}', i['name']) for i in get_all_routes()]
        routes = forms.ChoiceField(label='Направление', widget=forms.RadioSelect(), choices=choices)

    def __init__(self, *args, **kwargs):
        super(ReportFilterForm, self).__init__(*args, **kwargs)
        self.fields['routes'].empty_label = 'Выберите направление'
        # self.helper = FormHelper()
        # self.helper.layout = Layout(
        #     Div(
        #         Field('start_date', css_class='datetimepicker col-md-6 form-control '),
        #         Field('end_date', css_class='datetimepicker col-md-6 form-control '),
        #         css_class='row'
        #     ),
        #     Div(
        #         Field('routes', css_class='form-control'),
        #         css_class='row'
        #     ),
        # )