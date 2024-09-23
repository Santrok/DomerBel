from datetime import datetime, timedelta
from pprint import pprint

import requests
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from advertisement.models import Advertisement
from paid_service.forms import PaidForm
from paid_service.models import Service
from paid_service.serializers import PaidSerializer


# Create your views here.


def test_paid(request):
    store_id = '28723'
    secret_key = 'b08c17bc466d5cd391fc49cd77b6910e19c78b133dfceda65fcc4057af32b0af'
    url = 'https://checkout.bepaid.by/ctp/api/checkouts'
    if request.method == 'POST':
        form = PaidForm(request.POST)
        if form.is_valid():
            amount = 0
            description = []
            additional_data = {"advertisement": form.cleaned_data.get('advertisement').id}
            for service in form.cleaned_data.get('services'):
                amount += service.cost
                description.append(service.service_name)
                additional_data[service.key_word] = True
            payload = {
                "checkout": {
                    "test": True,
                    "transaction_type": "payment",
                    "attempts": 3,
                    "settings": {
                        "return_url": "http://127.0.0.1:8000/api/v1/notification/",
                        "success_url": "http://127.0.0.1:8000/api/v1/notification/",
                        "decline_url": "http://127.0.0.1:8000/",
                        "fail_url": "http://127.0.0.1:8000/",
                        "cancel_url": "http://127.0.0.1:8000/",
                        "notification_url": "http://127.0.0.1:8000/api/v1/notification/",
                        "button_text": "Оплатить",
                        "button_next_text": "Вернуться в магазин",
                        "language": "ru",
                        "card_notification_url": "https://your-card-notification-url.com",
                        "customer_fields": {
                            "visible": ["first_name", "last_name"],
                            "read_only": ["email", "phone"],
                        },
                        "credit_card_fields": {
                            "holder": "Rick Astley",
                            "read_only": ["holder"]
                        }
                    },
                    "payment_method": {
                        "types": ["credit_card"]
                    },
                    "order": {
                        "currency": "BYN",
                        "amount": int(amount * 100),
                        "description": f"Оплата услуг: {', '.join(description)}",
                        "tracking_id": "1212",
                        "additional_data": additional_data
                    },
                    "customer": {
                        "address": "Baker street 221b",
                        "country": "GB",
                        "city": "London",
                        "email": "jake@example.com",
                        "phone": "1234567890",
                    }
                }
            }

            response = requests.post(url, auth=HTTPBasicAuth(store_id, secret_key), json=payload)
            return redirect(response.json().get('checkout').get('redirect_url'))
        else:
            print(form.errors)
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@api_view(['POST'])
def send_paid(request):
    serializer = PaidSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        store_id = '28723'
        secret_key = 'b08c17bc466d5cd391fc49cd77b6910e19c78b133dfceda65fcc4057af32b0af'
        url = 'https://checkout.bepaid.by/ctp/api/checkouts'
        amount = 0
        description = []
        additional_data = {"advertisement": serializer.validated_data.get('advertisement').id}
        for service in serializer.validated_data.get('services'):
            amount += service.cost
            description.append(service.service_name)
            additional_data[service.key_word] = True
        payload = {
            "checkout": {
                "test": True,
                "transaction_type": "payment",
                "attempts": 3,
                "settings": {
                    "return_url": "http://127.0.0.1:8000/paid/api/notification/",
                    "success_url": "http://127.0.0.1:8000/paid/api/notification/",
                    "decline_url": "http://127.0.0.1:8000/",
                    "fail_url": "http://127.0.0.1:8000/",
                    "cancel_url": "http://127.0.0.1:8000/",
                    "notification_url": "http://127.0.0.1:8000/api/v1/notification/",
                    "button_text": "Оплатить",
                    "button_next_text": "Вернуться в магазин",
                    "language": "ru",
                    "card_notification_url": "https://your-card-notification-url.com",
                    "customer_fields": {
                        "visible": ["first_name", "last_name"],
                        "read_only": ["email", "phone"],
                    },
                    "credit_card_fields": {
                        "holder": "Rick Astley",
                        "read_only": ["holder"]
                    }
                },
                "payment_method": {
                    "types": ["credit_card"]
                },
                "order": {
                    "currency": "BYN",
                    "amount": int(amount * 100),
                    "description": f"Оплата услуг: {', '.join(description)}",
                    "tracking_id": "1212",
                    "additional_data": additional_data
                },
                "customer": {
                    "address": "Baker street 221b",
                    "country": "GB",
                    "city": "London",
                    "email": "jake@example.com",
                    "phone": "1234567890",
                }
            }
        }
        response = requests.post(url, auth=HTTPBasicAuth(store_id, secret_key), json=payload)
        if response.status_code == 201:
            return Response({"redirect": response.json().get('checkout').get('redirect_url')})
        else:
            raise serializers.ValidationError(
                {"errors": {"connect": "Ошибка связи с банком. Пожалуйста, попробуйте позже!"}})
    else:
        raise serializers.ValidationError({"errors": serializer.errors})


@api_view(['GET', 'POST'])
def get_bepaid(request):
    store_id = '28723'
    secret_key = 'b08c17bc466d5cd391fc49cd77b6910e19c78b133dfceda65fcc4057af32b0af'

    url = 'https://checkout.bepaid.by/ctp/api/checkouts/'
    token = request.query_params.get('token')
    information = requests.get(f'{url}{token}', auth=HTTPBasicAuth(store_id, secret_key))
    additional = information.json().get('checkout').get('order').get('additional_data')
    services = Service.objects.all()
    keys_date_of_deactivate = {"vip": "date_of_deactivate_vip",
                               "highlight_ad": "date_of_deactivate_highlight_ad",
                               "special_accommodation": "date_of_deactivate_special_accommodation",
                               "raise_in_search": "date_of_deactivate_raise_in_search"}
    accommodation = {}
    for service in services:
        if additional.get(service.key_word):
            accommodation[service.key_word] = additional.get(service.key_word)
            accommodation[keys_date_of_deactivate.get(service.key_word)] = datetime.now() + timedelta(days=service.validity_period)

    Advertisement.objects.filter(id=additional.get('advertisement')).update(**accommodation)

    return HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/')
