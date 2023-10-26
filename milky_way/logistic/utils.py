from .models import Office, Parcel, Transaction, CashCollection, City, ShipStatus
from milky_way.settings import logger
from datetime import datetime
import requests as rq
from milky_way.config import *
from django.db.models import Q


def make_transaction(parcel: Parcel):
    if parcel.payer.id == 1:
        office = parcel.from_office
    else:
        office = parcel.to_office
    new_transaction = Transaction.objects.create(
        parcel=parcel,
        amount=parcel.price,
        office=office,
    )
    logger.info(f'TRANSACTION WAS CREATED - {new_transaction}')
    return new_transaction


def get_balance(office: Office):
    transactions = Transaction.objects.filter(office=office)
    logger.info(f'TRANSACTIONS - {transactions}')
    sum_transactions = sum([i.amount for i in transactions])
    logger.info(f'SUM TRANSACTIONS - {sum_transactions}')
    cash_collections = CashCollection.objects.filter(office=office)
    logger.info(f'CASH COLLECTIONS - {cash_collections}')
    sum_cash_collections = sum([i.amount for i in cash_collections])
    logger.info(f'SUM CASH COLLECTIONS - {sum_cash_collections}')
    result = sum_transactions - sum_cash_collections
    return result


def get_routes(user_city):
    all_cities = City.objects.exclude(id=user_city.id)
    routes = []
    for city in all_cities:
        routes.append({
            'name': f'{user_city.name} - {city.name}',
            'from_city': user_city,
            'to_city': city
        })
    return routes


def get_all_routes():
    all_cities = City.objects.all()
    routes = []
    for city in all_cities:
        for other_city in all_cities[:]:
            if city != other_city:
                routes.append({
                    'name': f'{city.name} - {other_city.name}',
                    'from_city': city,
                    'to_city': other_city
                })
    return routes


def get_report(start_date: datetime, end_date: datetime, routes: list[dict]):
    from_offices = Office.objects.filter(city__in=[i['from_city'] for i in routes])
    logger.info(f'GET REPORT FROM OFFICES - {from_offices}')
    to_offices = Office.objects.filter(city__in=[i['to_city'] for i in routes])
    logger.info(f'GET REPORT TO OFFICES - {to_offices}')
    logger.info(f'END DATE - {end_date}')
    end_date = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=23, minute=59)
    parcels = Parcel.objects.filter(
        (Q(created_at__gte=start_date) & Q(created_at__lte=end_date)),
        from_office__in=from_offices,
        to_office__in=to_offices,
        # created_at__range=[start_date, end_date]
    )
    logger.info(f'PARCELS = {parcels}')
    results = {
        'parcels': {
            'total': len(parcels),
            'delivered': len(parcels.filter(ship_status__in=ShipStatus.objects.filter(id__in=[2, 4]))),
            'in_process': len(parcels.filter(ship_status__in=ShipStatus.objects.filter(id__in=[1, 3])))
        },
        'amounts': {
            'total': sum([i.price for i in parcels]),
            'paid': sum([i.price for i in parcels.filter(payment_status=True)]),
            'not_paid': sum([i.price for i in parcels.filter(payment_status=False)]),
        },
    }
    return results


def send_sms(phone, text):
    response = rq.get(f'https://api.iqsms.ru/messages/v2/send/?phone={phone}&text={text}&login={IQSMS_LOGIN}&password={IQSMS_PASSWORD}&sender={IQSMS_SENDER}')
    return response.text


def get_total_balance():
    offices = Office.objects.all()
    total_balance = sum([get_balance(office) for office in offices])
    return total_balance


