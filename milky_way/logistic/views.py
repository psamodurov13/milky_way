from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from milky_way.settings import logger
from .models import *


@login_required
def index(request):
    context = {
        'title': 'Логистическая компания «Млечный путь»',
    }
    user_groups = [i.name for i in request.user.groups.all()]
    if 'Сотрудники' in user_groups:
        context['template'] = 'Сотрудник'
        context['user'] = request.user
        user_office = request.user.office
        user_city = user_office.city
        logger.info(f'USER CITY {user_city}')
        all_cities = City.objects.exclude(id=user_city.id)
        routes = []
        for city in all_cities:
            routes.append({
                'name': f'{user_city.name} - {city.name}',
                'from_city': user_city,
                'to_city': city
            })
        logger.info(f'ROUTES - {routes}')
        logger.info(f'USER OFFICE - {user_office}')
        context['office'] = user_office
        context['routes'] = routes
        # logger.info(request.user)
        return render(request, 'logistic/index-employee.html', context)
    elif request.user.is_superuser:
        context['template'] = 'Админ'
        return render(request, 'logistic/index-admin.html', context)
    else:
        context = {
            'title': 'Ошибка',
        }
    return render(request, 'logistic/index.html', context)


# contact_list = Women.objects.all()
# paginator = Paginator(contact_list, 3)
#
# page_number = request.GET.get('page')
# page_obj = paginator.get_page(page_number)
#
# return render(request, 'women/about.html', {'page_obj': page_obj, 'menu': menu, 'title': 'О сайте'})
#
#
# {% for contact in page_obj %}
# <p>{{ contact }}</p>
# {% endfor %}

def login_page(request):
    context = {}
    form = UserLoginForm()
    context['form'] = form
    return render(request, 'logistic/login_page.html', context)


# def login_page(request):
#     login_form = UserLoginForm()
#     context = {
#         'login_form': login_form,
#     }
#     return render(request, 'bots/login.html', context)


def user_login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(data=request.POST)
        # register_form = UserRegisterForm()
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'Вход выполнен')
        else:
            # messages.error(request, 'Вход не выполнен, проверьте форму')
            # return redirect('login_page')
            return render(request, 'logistic/login_page.html', {'form': login_form})
    if request.user.is_superuser:
        return redirect('index')
    else:
        return redirect('index')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('index')
