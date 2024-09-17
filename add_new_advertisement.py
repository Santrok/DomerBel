import os
from django.core.files import File

import django

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Django
django.setup()

from advertisement.models import Advertisement, PhotoAdvertisement, Store

new_advertisement = Advertisement(author_id=4564, additional_information={'': 'потеряно'}, title='Морж',
                  bearer='Частное лицо', contact_name='Alexander', email='admin@super.com',
                  phone_num='+375447113036', description='Привет', video_link='',
                  category_id=101, region_id=6)

new_advertisement.save()

preview_img = '/home/nemo/Загрузки/images.jpeg'
with open(preview_img, 'rb') as f:
    new_advertisement.preview_image = File(f)
    new_advertisement.save()

other_images = ['/home/nemo/Загрузки/1626630161_b_.jpg', '/home/nemo/Загрузки/паспорт.jpg']
for photo in other_images:
    with open(photo, 'rb') as f:
        additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
        additional_photo.save()

print('да')

