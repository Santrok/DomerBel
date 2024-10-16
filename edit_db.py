import os
import django
from datetime import datetime
from django.db.models import F, Value
from django.db.models.functions import Replace

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Django
django.setup()

from advertisement.models import Advertisement, PhotoAdvertisement, Store

advertisements = Advertisement.objects.filter(preview_image__endswith='.jpg')
print('Всего объявлений:', advertisements.count())
data_start = datetime.now()
advertisements.update(preview_image=Replace(F('preview_image'), Value('.jpg'), Value('.avif')))
print(datetime.now() - data_start)

photo_advertisements = PhotoAdvertisement.objects.filter(photo__endswith='.jpg')
print('Всего фото объявлений:', photo_advertisements.count())
data_start = datetime.now()
photo_advertisements.update(photo=Replace(F('photo'), Value('.jpg'), Value('.avif')))
print(datetime.now() - data_start)

stores = Store.objects.filter(logo_image__endswith='.jpg')
print('Всего фото объявлений:', stores.count())
data_start = datetime.now()
stores.update(logo_image=Replace(F('logo_image'), Value('.jpg'), Value('.avif')))
print(datetime.now() - data_start)