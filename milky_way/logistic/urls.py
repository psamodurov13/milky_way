from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('create-new-parcel', views.create_new_parcel, name='create_new_parcel'),
    path('employees', views.EmployeesView.as_view(), name='employees'),
    path('accounting', views.accounting, name='accounting'),
    path('reports', views.reports, name='reports'),
    path('change-route/<int:from_city>/<int:to_city>', views.change_route, name='change_route')

]


