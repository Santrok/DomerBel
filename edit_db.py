import os
import django
from datetime import datetime
from django.db.models import F, Value
from django.db.models.functions import Replace

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Django
django.setup()

from advertisement.models import Advertisement, PhotoAdvertisement

advertisements = Advertisement.objects.all()

# data_start = datetime.now()
# print('Всего объявлений:', advertisements.count())
# count_advertisements, count_advertisements_no_preview, count_advertisements_avif = 0, 0, 0
#
# for advertisement in advertisements:
#     if advertisement.preview_image and advertisement.preview_image.url.endswith('.jpg'):
#         # Меняем расширение в имени файла с .jpg на .avif
#         new_image_path = advertisement.preview_image.name.replace('.jpg', '.avif')
#         # Обновляем поле preview_image на новое имя файла
#         advertisement.preview_image.name = new_image_path
#         # Сохраняем изменения в базе данных
#         advertisement.save()
#         # Считаем измененные файлы
#         count_advertisements += 1
#     if not advertisement.preview_image:
#         # Считаем поля там где нет картинок
#         count_advertisements_no_preview += 1
#     elif advertisement.preview_image.url.endswith('.avif'):
#         # Считаем поля там где расширение уже avif
#         count_advertisements_avif += 1
#
# data_end = datetime.now()
# print('Измененных:', count_advertisements, ';',
#       'Без фото:', count_advertisements_no_preview, ';',
#       'avif:', count_advertisements_avif, ';',
#       'Всего:', count_advertisements + count_advertisements_avif + count_advertisements_no_preview, ';',
#       'Ушло времени', data_end - data_start)

photo_advertisements = PhotoAdvertisement.objects.all()
photo_advertisements1 = PhotoAdvertisement.objects.filter(photo__endswith='.jpg')
print(photo_advertisements.count(), photo_advertisements1.count())
# data_start = datetime.now()
# print('Всего фото для объявлений:', photo_advertisements.count())
# count_photo_advertisements, photo_advertisements_avif = 0, 0


photo_advertisements.filter(photo__endswith='.jpg').update(
    photo=Replace(F('photo'), Value('.jpg'), Value('.avif'))
)


# for photo_advertisement in photo_advertisements.filter(id=680):
#     if photo_advertisement.photo and photo_advertisement.photo.url.endswith('.jpg'):
#         # Меняем расширение в имени файла с .jpg на .avif
#         new_image_path = photo_advertisement.photo.name.replace('.jpg', '.avif')
#         # Обновляем поле preview_image на новое имя файла
#         photo_advertisement.photo.name = new_image_path
#         # Сохраняем изменения в базе данных
#         photo_advertisement.save()
#         # Считаем измененные файлы
#         count_photo_advertisements += 1
#     elif photo_advertisement.photo.url.endswith('.avif'):
#         # Считаем поля там где расширение уже avif
#         photo_advertisements_avif += 1

# data_end = datetime.now()
# print('Измененных:', count_photo_advertisements, ';',
#       'avif:', photo_advertisements_avif, ';',
#       'Всего:', count_photo_advertisements + photo_advertisements_avif, ';',
#       'Ушло времени', data_end - data_start)
