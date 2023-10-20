from .models import Office, Parcel, Transaction, CashCollection
from milky_way.settings import logger


def make_transaction(parcel: Parcel):
    if parcel.payer.name == 'Отправитель':
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

