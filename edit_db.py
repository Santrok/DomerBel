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

for advertisement in advertisements.filter(id=30):
    if advertisement.preview_image and advertisement.preview_image.url.endswith('.jpg'):
        print('id: ', advertisement.id)
        # new_url = advertisement.preview_image.path.replace('.jpg', '.avif')
        # with open(new_url, 'rb') as f:
        #     advertisement.preview_image.save(os.path.basename(new_url), File(f))
        # advertisement.save()
        # count_advertisements += 1
        new_image_path = advertisement.preview_image.name.replace('.jpg', '.avif')

        # Обновляем поле preview_image на новое имя файла
        advertisement.preview_image.name = new_image_path

        # Сохраняем изменения в базе данных
        advertisement.save()
        print(advertisement.preview_image.url)

print('count: ',count_advertisements)