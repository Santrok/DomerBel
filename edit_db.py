import os
import django
from django.core.files import File
from PIL import Image

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Django
django.setup()

from advertisement.models import Advertisement

advertisements = Advertisement.objects.all()

print(advertisements.count())
count_advertisements = 0

for advertisement in advertisements:
    if advertisement.preview_image and advertisement.preview_image.url.endswith('.jpg'):

        # Меняем расширение в имени файла с .jpg на .avif
        new_image_path = advertisement.preview_image.name.replace('.jpg', '.avif')

        # Обновляем поле preview_image на новое имя файла
        advertisement.preview_image.name = new_image_path

        # Сохраняем изменения в базе данных
        advertisement.save()

        count_advertisements += 1

print('count: ',count_advertisements)