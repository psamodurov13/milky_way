from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.urls import reverse_lazy
from .utils import make_transaction, get_balance, get_routes, get_all_routes, get_report, send_sms, get_total_balance
from .forms import *
from django.contrib.auth.decorators import login_required
from milky_way.settings import logger
from .models import *
from django.db.models import Q
from datetime import datetime, timedelta

from barcode import generate
from barcode.writer import ImageWriter



@login_required
def index(request):
    context = {
        'title': 'Логистическая компания «Млечный путь»',
    }
    search_query = request.GET.get('search', None)
    logger.info(f'SEARCH - "{search_query}"')
    get_params = request.GET
    if 'search' in get_params and get_params['search'] == '':
        new_url = request.path_info
        if not new_url.endswith('/'):
            new_url += '/'
        return redirect(new_url)
    user_groups = [i.name for i in request.user.groups.all()]
    logger.info(f'REQUEST - {request.path_info}')
    if 'Сотрудники' in user_groups:

        user_office = request.user.office
        balance = get_balance(user_office)
        logger.info(f'BALANCE - {balance}')
        user_city = user_office.city
        logger.info(f'USER CITY {user_city}')
        routes = get_routes(user_city)
        if 'route' not in request.session.keys():
            current_route = {'from_id': routes[0]['from_city'].id, 'to_id': routes[0]['to_city'].id}
            request.session['route'] = current_route
        else:
            current_route = request.session['route']
        logger.info(f'ROUTES - {routes}')
        if 'way' not in request.session.keys():
            current_way = 'sent'
            request.session['way'] = current_way
        else:
            current_way = request.session['way']
        logger.info(f'USER OFFICE - {user_office}')
        if current_way == 'sent':
            all_parcels = Parcel.objects.filter(
                from_office__in=City.objects.get(id=current_route['from_id']).offices.all(),
                to_office__in=City.objects.get(id=current_route['to_id']).offices.all(),
            )
        else:
            all_parcels = Parcel.objects.filter(
                to_office__in=City.objects.get(id=current_route['from_id']).offices.all(),
                from_office__in=City.objects.get(id=current_route['to_id']).offices.all(),
            )
        if search_query and search_query != '':
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
        paginator = Paginator(parcels, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        logger.info(f'PARCELS - {parcels}')
        if search_query:
            context['search_query'] = search_query
        context['user'] = request.user
        context['office'] = user_office
        context['routes'] = routes
        context['new_parcel_form'] = NewParcelForm()
        context['customers'] = Customer.objects.all()
        context['search_form'] = search_form
        context['way'] = current_way
        context['balance'] = balance
        return render(request, 'logistic/index-employee.html', context)
    elif request.user.is_superuser:
        routes = get_all_routes()
        logger.info(f'ALL ROUTES - {routes}')
        if 'route' not in request.session.keys():
            current_route = {'from_id': routes[0]['from_city'].id, 'to_id': routes[0]['to_city'].id}
            request.session['route'] = current_route
        else:
            current_route = request.session['route']
        logger.info(f'ROUTES - {routes}')
        logger.info(f'current_route - {current_route}')
        try:
            all_parcels = Parcel.objects.filter(
                from_office__in=City.objects.get(id=current_route['from_id']).offices.all(),
                to_office__in=City.objects.get(id=current_route['to_id']).offices.all(),
            )
        except Exception:
            logger.exception(Exception)
            current_route = {'from_id': routes[0]['from_city'].id, 'to_id': routes[0]['to_city'].id}
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
        paginator = Paginator(parcels, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        logger.info(f'PARCELS - {parcels}')
        context['search_query'] = search_query
        context['routes'] = routes
        context['search_form'] = search_form
        context['balance'] = get_total_balance()
        return render(request, 'logistic/index-admin.html', context)
    else:
        context = {
            'title': 'Ошибка',
        }
    return render(request, 'logistic/index.html', context)


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
        form = NewParcelForm(request.POST)
        logger.info(f'METHOD POST, REQUEST - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            for customer in ['from_customer', 'to_customer']:
                if '/' in form_data[customer]:
                    customer_name = form_data[customer].split(' / ')[1]
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
                ship_status=ShipStatus.objects.get(id=4),
                price=form_data['price'],
                created_by=request.user,
            )
            if new_parcel.payer.id == 1:
                new_parcel.payment_status = True
                new_parcel.save()
                new_transaction = make_transaction(new_parcel)
                logger.info(f'NEW TRANSACTION - {new_transaction}')
            logger.info(f'Посылка создана - {new_parcel}')
            messages.success(request, 'Посылка создана')
            if 'send-print-button' in request.POST['button-clicked']:
                logger.info(f'WITH PRINT')
                barcode_file = generate('code128', str(new_parcel.id), writer=ImageWriter(), output=f'./media/barcode-{new_parcel.id}')
                text = f'''<p>{new_parcel.to_customer.name}</p>                       
<p>{str(new_parcel.from_customer.phone)}</p>
<p>{str(new_parcel.to_customer.phone)}</p>
<p>Код: <b>{new_parcel.id}</b></p>
<p>Стоимость: {new_parcel.price}</p>
<p>Плательщик: {new_parcel.payer.name}</p>
'''

                return JsonResponse({'error': False, 'message': 'Посылка создана',
                                     # 'barcode': f"/media/barcode-{new_parcel.id}.png",
                                     'barcode': text})
            else:
                logger.info(f'WITHOUT PRINT')
                return JsonResponse({'error': False, 'message': 'Посылка создана', 'barcode': None})
        else:
            logger.info(f'FORM IS NOT VALID. ERRORS - {form.errors}')
            return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, допущена ошибка'})
    else:
        messages.error(request, 'НЕПРЕДВИДЕННАЯ ОШИБКА')
        logger.debug(f'НЕПРЕДВИДЕННАЯ ОШИБКА. МЕТОД GET НА URL ОТПРАВКИ ФОРМЫ')
        logger.info(f'REQUEST {request}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_cash_collection(request):
    logger.info(f'SEND FORM CREATE CASH COLLECTION')
    if request.method == 'POST':
        form = CashCollectionForm(request.POST)
        logger.info(f'METHOD POST, REQUEST - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FORM DATA - {form_data}')
            new_cash_collection = CashCollection.objects.create(
                amount=form_data['amount'],
                office=form_data['office']
            )
            logger.info(f'NEW TRANSACTION - {new_cash_collection}')
            messages.success(request, f'Новая инкассация на {new_cash_collection.amount} руб. создана')
            return JsonResponse({'error': False, 'message': 'Инкассация создана'})
        else:
            logger.info(f'FORM IS NOT VALID. ERRORS - {form.errors}')
            return JsonResponse({'error': True, 'errors': form.errors, 'message': 'Проверьте форму, допущена ошибка'})
    else:
        messages.error(request, 'НЕПРЕДВИДЕННАЯ ОШИБКА')
        logger.debug(f'НЕПРЕДВИДЕННАЯ ОШИБКА. МЕТОД GET НА URL ОТПРАВКИ ФОРМЫ')
        logger.info(f'REQUEST {request}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def accounting(request):
    offices = Office.objects.all()
    result = []
    for office in offices:
        result.append({
            'office': office,
            'balance': get_balance(office)
        })
    total_balance = sum([i['balance'] for i in result])
    context = {
        'offices': result,
        'total_balance': total_balance
    }
    form = CashCollectionForm()
    context['form'] = form
    return render(request, 'logistic/accounting.html', context)


def reports(request):
    context = {
        'title': 'Отчет'
    }
    logger.info(f'REQUEST>POST - {request.POST}')
    if request.POST:
        form = ReportFilterForm(request.POST)
        logger.info(f'REQUEST DATA - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            start_date = form_data['start_date']
            end_date = form_data['end_date']
            from_city_id, to_city_id = form_data['routes'].split('-')
            from_city = City.objects.get(id=from_city_id)
            to_city = City.objects.get(id=to_city_id)
            route = {
                'name': f'{from_city.name} - {to_city.name}',
                'from_city': from_city,
                'to_city': to_city
            }
            routes = [route]
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        routes = get_all_routes()
        form = ReportFilterForm(
            initial={
                'start_date': start_date,
                'end_date': end_date,
            }
        )
    context['form'] = form
    report_data = get_report(start_date, end_date, routes)
    logger.info(f'REPORT DATA - {report_data}')
    context['report'] = report_data
    return render(request, 'logistic/reports.html', context)


def change_route(request, from_city, to_city):
    # from_city, to_city = route_id.split('to')
    current_route = {'from_id': from_city, 'to_id': to_city}
    request.session['route'] = current_route
    return redirect('index')


def change_way(request, way):
    # from_city, to_city = route_id.split('to')
    current_way = way
    request.session['way'] = current_way
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def receive_to_office(request):
    logger.info(f'RECEIVE TO OFFICE STARTED')
    route = request.session['route']
    delivering_parcels = Parcel.objects.filter(
        from_office=City.objects.get(id=route['to_id']).offices.all()[0],
        to_office=City.objects.get(id=route['from_id']).offices.all()[0],
        ship_status=ShipStatus.objects.get(id=3),
    )
    all_sms_tasks_to = []
    all_sms_tasks_from = []
    for parcel in delivering_parcels:
        parcel.ship_status = ShipStatus.objects.get(id=1)
        parcel.save()
        sms_text = f'''Ваша посылка доставлена в офис службы доставки "Млечный путь". Код-{parcel.id}. '''
        all_sms_tasks_to.append(send_sms(str(parcel.to_customer.phone), sms_text))
        all_sms_tasks_from.append(send_sms(str(parcel.from_customer.phone), sms_text))
    logger.info(f'SMS TO {all_sms_tasks_to}')
    logger.info(f'SMS FROM {all_sms_tasks_from}')
    messages.success(request, f'Принято посылок - {len(delivering_parcels)} ')
    logger.info(f'DELIVERING PARCELS - {delivering_parcels}')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def send_to_office(request):
    logger.info(f'SEND TO OFFICE STARTED')
    route = request.session['route']
    parcels_for_send = Parcel.objects.filter(
        from_office=City.objects.get(id=route['from_id']).offices.all()[0],
        to_office=City.objects.get(id=route['to_id']).offices.all()[0],
        ship_status=ShipStatus.objects.get(id=4),
    )
    for parcel in parcels_for_send:
        parcel.ship_status = ShipStatus.objects.get(id=3)
        parcel.save()
    messages.success(request, f'Отправлено посылок - {len(parcels_for_send)} ')
    logger.info(f'SENT PARCELS - {parcels_for_send}')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def deliver_parcel(request, parcel_id):
    parcel = Parcel.objects.get(id=parcel_id)
    if not parcel.payment_status and parcel.payer.id == 2:
        parcel.payment_status = True
        new_transaction = make_transaction(parcel)
        logger.info(f'NEW TRANSACTION - {new_transaction}')
    parcel.ship_status = ShipStatus.objects.get(id=2)
    parcel.complete_date = datetime.now()
    parcel.delivered_by = request.user
    parcel.save()
    messages.success(request, 'Посылка вручена')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_object_info(request):
    object_id = request.GET.get('object_id')
    parcel = Parcel.objects.get(id=object_id)
    object_info = {
        'name': parcel.to_customer.name,
        'phone': str(parcel.to_customer.phone),
        'code': parcel.id,
        'price': parcel.price,
        'payer': parcel.payer.name
    }
    html_response = f'''
        <table class="table table-hover">
          <tbody>
            <tr>
              <th>ФИО</th>
              <td>{ object_info["name"] }</td>
            </tr>
            <tr>
              <th>Телефон</th>
              <td>{ object_info["phone"] }</td>
            </tr>
            <tr>
              <th>Код</th>
              <td>{ object_info["code"] }</td>
            </tr>
            <tr>
              <th>Стоимость доставки</th>
              <td>{ object_info["price"] }</td>
            </tr>
            <tr>
              <th>Плательщик</th>
              <td>{ object_info["payer"] }</td>


            </tr>
          </tbody>
        </table>
        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Отмена</button>
        <a href="deliver-parcel/{parcel.id}" type="button" class="btn btn-primary deliver-parcel-button btn-sm">Выдать</a>

'''
    return JsonResponse({'html_response': html_response})


