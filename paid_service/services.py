import requests
from requests.auth import HTTPBasicAuth

from config.settings import env_keys


def send_payment_request(url, store_id, secret_key, data, user_email, token=''):
    """
    Отправляет запрос на оплату и обрабатывает возможные ошибки.
    """
    payload = _create_payment_payload(data, user_email)
    try:
        response = requests.post(f"{url}{token}", auth=HTTPBasicAuth(store_id, secret_key), json=payload)
        response.raise_for_status()  # Вызывает исключение для статусов 4xx и 5xx
        return response
    except requests.exceptions.RequestException:
        return None


def _create_payment_payload(data, user_email):
    """
    Создает тело запроса на api эквайринга.
    """
    amount, description, additional_data, title_ad = _calculate_payment_details(data)
    payload = {
            "checkout": {
                "test": {env_keys.get('PAID_SERVICE_TEST')},
                "transaction_type": "payment",
                "attempts": 3,
                "settings": {
                    "return_url": f"{env_keys.get('URL')}",
                    "success_url": f"{env_keys.get('URL')}",
                    "decline_url": f"{env_keys.get('URL')}",
                    "fail_url": f"{env_keys.get('URL')}",
                    "cancel_url": f"{env_keys.get('URL')}",
                    "notification_url": f"{env_keys.get('URL')}/api/v1/notification/",
                    "button_text": "Оплатить",
                    "button_next_text": "Вернуться в магазин",
                    "language": "ru",
                    "card_notification_url": "https://your-card-notification-url.com",
                    "customer_fields": {
                        "visible": ["email",],
                        "read_only": ["first_name",
                                      "last_name",
                                      "phone",
                                      "address",
                                      "city",
                                      "state",
                                      "zip",
                                      "phone",
                                      "country",
                                      "birth_date",
                                      "taxpayer_id"],
                    },
                    "credit_card_fields": {  # удалить при деплое
                        "holder": "Test User",
                        "read_only": ["holder"]
                    }
                },
                "payment_method": {
                    "types": ["credit_card"]
                },
                "order": {
                    "currency": "BYN",
                    "amount": int(amount * 100),
                    "description": f"Оплата услуг для объявления '{title_ad}': {', '.join(description)}. Для оплаты введите номер тестовой карты 4012000000001006, CVC - 111, дата срока действия не должна быть прошедшим.",
                    "additional_data": additional_data
                },
                "customer": {
                    "email": user_email,
                }
            }
        }
    return payload


def _calculate_payment_details(serializer):
    """
    Вычисляет сумму, описание и дополнительные данные для создания нагрузки оплаты.
    """
    amount = 0
    description = []
    title_ad = serializer.validated_data.get('advertisement').title
    additional_data = {"advertisement": serializer.validated_data.get('advertisement').id,
                       "advertisement_title": title_ad}

    for service in serializer.validated_data.get('services'):
        amount += service.cost
        description.append(service.service_name)
        additional_data[service.key_word] = True

    return amount, description, additional_data, title_ad
