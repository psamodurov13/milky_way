from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from django.contrib.auth.decorators import login_required
from milky_way.settings import logger
from .models import *
from django.db.models import Q
from django.views.generic import ListView


@login_required
def index(request):
    context = {
        'title': 'Логистическая компания «Млечный путь»',
    }
    user_groups = [i.name for i in request.user.groups.all()]
    if 'Сотрудники' in user_groups:

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
        if 'route' not in request.session.keys():
            current_route = {'from_id': routes[0]['from_city'].id, 'to_id': routes[0]['to_city'].id}
            request.session['route'] = current_route
        else:
            current_route = request.session['route']
        logger.info(f'ROUTES - {routes}')
        logger.info(f'USER OFFICE - {user_office}')
        all_parcels = Parcel.objects.filter(
            from_office__in=City.objects.get(id=current_route['from_id']).offices.all(),
            to_office__in=City.objects.get(id=current_route['to_id']).offices.all(),
        )

        search_query = request.GET.get('search', None)
        logger.info(f'SEARCH - {search_query}')
        if search_query:
            search_form = SearchParcelsForm(request.GET)
            if search_query.isdigit():
                parcels = all_parcels.filter(id=int(search_query))
            else:
                parcels = all_parcels.filter(
                    Q(to_customer__name__icontains=search_query) |
                    Q(from_customer__name__icontains=search_query)
                )
            logger.info(f'GET PARCELS - {parcels}')
        else:
            search_form = SearchParcelsForm()
            parcels = all_parcels
        paginator = Paginator(parcels, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        logger.info(f'PARCELS - {parcels}')
        context['search_query'] = search_query
        context['user'] = request.user
        context['office'] = user_office
        context['routes'] = routes
        context['new_parcel_form'] = NewParcelForm()
        context['customers'] = Customer.objects.all()
        context['search_form'] = search_form
        return render(request, 'logistic/index-employee.html', context)
    elif request.user.is_superuser:
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
        logger.info(f'ALL ROUTES - {routes}')
        if 'route' not in request.session.keys():
            current_route = {'from_id': routes[0]['from_city'].id, 'to_id': routes[0]['to_city'].id}
            request.session['route'] = current_route
        else:
            current_route = request.session['route']
        logger.info(f'ROUTES - {routes}')
        all_parcels = Parcel.objects.filter(
            from_office__in=City.objects.get(id=current_route['from_id']).offices.all(),
            to_office__in=City.objects.get(id=current_route['to_id']).offices.all(),
        )
        search_query = request.GET.get('search', None)
        logger.info(f'SEARCH - {search_query}')
        if search_query:
            search_form = SearchParcelsForm(request.GET)
            if search_query.isdigit():
                parcels = all_parcels.filter(id=int(search_query))
            else:
                parcels = all_parcels.filter(
                    Q(to_customer__name__icontains=search_query) |
                    Q(from_customer__name__icontains=search_query)
                )
            logger.info(f'GET PARCELS - {parcels}')
        else:
            search_form = SearchParcelsForm()
            parcels = all_parcels
        paginator = Paginator(parcels, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        logger.info(f'PARCELS - {parcels}')
        context['search_query'] = search_query
        context['routes'] = routes
        context['search_form'] = search_form
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


def user_login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'Вход выполнен')
        else:
            return render(request, 'logistic/login_page.html', {'form': login_form})
    if request.user.is_superuser:
        return redirect('index')
    else:
        return redirect('index')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('index')


def create_new_parcel(request):
    logger.info(f'SEND FORM CREATE NEW PARCEL')
    if request.method == 'POST':
        form = NewParcelForm(request.POST, request)
        logger.info(f'METHOD POST, REQUEST - {request.POST}')
        # form_data = form.cleaned_data
        # logger.info(f'FORM DATA - {form_data}')
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            for customer in ['from_customer', 'to_customer']:
                if '/' in form_data[customer]:
                    customer_name = form_data[customer].split(' / ')[0]
                    customer_phone = form_data[f'{customer}'].split(' / ')[-1]
                    logger.info(f'CUSTOMER NAME {customer_name}, CUSTOMER PHONE {customer_phone}')
                    customer_object = Customer.objects.get(name=customer_name, phone=customer_phone)
                    logger.info(f'CUSTOMER OBJECT {customer_object}')
                else:
                    customer_object = Customer.objects.create(
                        name=form_data[customer],
                        phone=form_data[f'{customer}_phone']
                    )
                    logger.info(f'NEW CUSTOMER WAS CREATED - {customer_object}')
                if customer == 'from_customer':
                    from_customer = customer_object
                else:
                    to_customer = customer_object
            logger.info(f'FROM {from_customer}')
            logger.info(f'TO {to_customer}')
            # Пока в городе присутствует только один офис, данный код будет работать.
            # Далее надо будет добавить поле для выбора офиса доставки
            logger.info(f'REQUEST USER - {request.user}')
            route = request.session['route']
            logger.info(f'REQUEST ROUTE - {route}')
            new_parcel = Parcel.objects.create(
                from_office=City.objects.get(id=route['from_id']).offices.all()[0],
                from_customer=from_customer,
                to_office=City.objects.get(id=route['to_id']).offices.all()[0],
                to_customer=to_customer,
                payer=Payer.objects.get(id=int(form_data['payer'])),
                payment_status=form_data['payment_status'],
                ship_status=ShipStatus.objects.get(id=3),
                price=form_data['price'],
                created_by=request.user,
            )
            logger.info(f'Посылка создана - {new_parcel}')

            messages.success(request, 'Посылка создана')
            return JsonResponse({'error': False, 'message': 'Посылка создана'})
            # return redirect('index')
        else:
            logger.info(f'FORM IS NOT VALID. ERRORS - {form.errors}')
            return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, допущена ошибка'})

            # return render(request, 'logistic/index-employee.html', context)
    else:
        messages.error(request, 'НЕПРЕДВИДЕННАЯ ОШИБКА')
        logger.debug(f'НЕПРЕДВИДЕННАЯ ОШИБКА. МЕТОД GET НА URL ОТПРАВКИ ФОРМЫ')
        logger.info(f'REQUEST {request}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class EmployeesView(ListView):
    model = User
    paginate_by = 20
    template_name = 'logistic/employees_list.html'
    context_object_name = 'employees'
    ordering = 'id'


def accounting(request):
    pass


def reports(request):
    pass


def change_route(request, from_city, to_city):
    # from_city, to_city = route_id.split('to')
    current_route = {'from_id': from_city, 'to_id': to_city}
    request.session['route'] = current_route
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# def send_form(request):
#     if request.method == 'POST':
#         form = ApplicationForm(request.POST, request=request)
#         if form.is_valid():
#             form_data = form.cleaned_data
#             new_application = Application.objects.create(**form_data)
#             print(f'NEW {new_application} - {new_application.__dict__}')
#             new_application.save()
#             return JsonResponse({'error': False, 'message': 'Заявка отправлена'})
#         else:
#             return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, телефон указан некорректно'})
