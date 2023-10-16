from django.contrib import admin
from milky_way.utils import BaseAdmin
from .models import *


class CityAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name', )


class OfficeAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'address')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'address')
    list_filter = ('city',)


class PayerAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


class CustomerAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'telegram')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'email', 'phone', 'telegram')


class ShipStatusAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


class ParcelAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'from_office', 'to_office', 'ship_status', 'price', 'to_customer', 'created_at',
                    'complete_date', 'payment_status')
    list_display_links = ('id',)
    search_fields = ('name', 'from_customer', 'to_customer')
    list_filter = ('from_office', 'to_office', 'ship_status', 'payment_status')


class TransactionAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'parcel', 'amount', 'office', 'date_time', 'cash_collected', 'cash_collection')
    list_display_links = ('id',)
    search_fields = ('id', 'parcel')
    list_filter = ('office', 'cash_collected', 'cash_collection',)


class CashCollectionAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('id', 'date_time', 'office', 'amount',)
    list_display_links = ('id',)
    search_fields = ('id', )
    list_filter = ('office', )


admin.site.register(City, CityAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Payer, PayerAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ShipStatus, ShipStatusAdmin)
admin.site.register(Parcel, ParcelAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CashCollection, CashCollectionAdmin)
