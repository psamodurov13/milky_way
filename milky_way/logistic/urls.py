from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('create-new-parcel', views.create_new_parcel, name='create_new_parcel'),
    path('accounting', views.accounting, name='accounting'),
    path('reports', views.reports, name='reports'),
    path('change-route/<int:from_city>/<int:to_city>', views.change_route, name='change_route'),
    path('change-way/<str:way>', views.change_way, name='change_way'),
    path('send-to-office/', views.send_to_office, name='send_to_office'),
    path('receive-to-office/', views.receive_to_office, name='receive_to_office'),
    path('deliver-parcel/<int:parcel_id>', views.deliver_parcel, name='deliver_parcel'),
    path('get_object_info/', views.get_object_info, name='get_object_info'),
    path('create-cash-collection', views.create_cash_collection, name='create_cash_collection'),
]


