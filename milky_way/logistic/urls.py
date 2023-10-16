from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    # path('register', views.user_register, name='register'),
    path('logout', views.user_logout, name='logout'),
]


