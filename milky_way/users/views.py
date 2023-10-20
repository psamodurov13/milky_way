from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView
from .models import User
from milky_way.utils import CustomStr
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from milky_way.settings import logger
from django.contrib.auth.models import Group


class EmployeesView(ListView):
    model = User
    paginate_by = 20
    template_name = 'users/employees_list.html'
    context_object_name = 'employees'
    ordering = 'id'

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomUserCreationForm()
        context['create_user_url'] = reverse('create_new_user')
        return context

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)  # Создайте экземпляр формы, передав POST данные
        if form.is_valid():
            new_user = form.save()
            logger.info(f'NEW USER - {new_user}')
            group = Group.objects.get(name='Сотрудники')
            new_user.groups.add(group)
            return JsonResponse({'error': False, 'message': 'Пользователь создан'})
        # Если форма не прошла валидацию, вы можете вернуть страницу с ошибками
        return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, допущена ошибка'})


class EditUser(CustomStr, UpdateView):
    model = get_user_model()
    # form_class = CustomUserChangeForm
    fields = ["username", "last_name", "first_name", "second_name", "email", "phone", "office"]
    success_url = reverse_lazy('employees')
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Сотрудник изменен')
        return super().form_valid(form)


class DeleteEmployee(CustomStr, DeleteView):
    model = User
    success_url = reverse_lazy('employees')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, 'Сотрудник удален')
        return HttpResponseRedirect(success_url)


def change_password(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль успешно изменен')
            return redirect('employees')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'users/change_password.html', {'form': form, 'user': user})


def create_new_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'error': False, 'message': 'Посылка создана'})
        else:
            logger.info(f'FORM IS NOT VALID. ERRORS - {form.errors}')
            return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, допущена ошибка'})
    else:
        logger.debug(f'THERE IS NOT POST REQUEST IN create_new_user FUNCTION')
        return redirect('employees')


