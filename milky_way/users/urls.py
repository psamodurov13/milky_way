from django.urls import path

from . import views

urlpatterns = [
    path('', views.EmployeesView.as_view(), name='employees'),
    path('<int:pk>', views.EditUser.as_view(), name='edit_user'),
    path('delete-user/<int:pk>', views.DeleteEmployee.as_view(), name='delete_user'),
    path('change-password/<int:user_id>', views.change_password, name='change_password'),
    path('create-new-user/', views.create_new_user, name='create_new_user'),
]





