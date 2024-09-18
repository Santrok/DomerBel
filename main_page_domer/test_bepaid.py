import requests
from requests.auth import HTTPBasicAuth




store_id = '28723'
secret_key = 'b08c17bc466d5cd391fc49cd77b6910e19c78b133dfceda65fcc4057af32b0af'

url = 'https://checkout.bepaid.by/ctp/api/checkouts'

payload = {
  "checkout": {
    "test": True,
    "transaction_type": "payment",
    "attempts": 3,
    "settings": {
      "return_url": "http://127.0.0.1:8000/",
      "success_url": "http://127.0.0.1:8000/",
      "decline_url": "http://127.0.0.1:8000/",
      "fail_url": "http://127.0.0.1:8000/",
      "cancel_url": "http://127.0.0.1:8000/",
      "notification_url": "http://127.0.0.1:8000/notification/",
      "button_text": "Привязать карту",
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
      "amount": 5000,
      "description": "Много букв товар",
      "tracking_id": "1212",
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


if response.status_code == 200 or response.status_code == 201:
    print("Запрос успешно выполнен")
    print(response.json())
else:
    print("Произошла ошибка при выполнении запроса")
    print(response.status_code)
    print(response.text)