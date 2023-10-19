from .models import Office, Parcel, Transaction
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

