import random
import os
import pillow_avif
from io import BytesIO
from datetime import date
from uuid import uuid4
from slugify import slugify
from PIL import Image, ImageDraw, ImageFont
from hashlib import md5
from django.core.files.base import ContentFile


# from .models import Advertisement

def upload_to(instance, filename):
    """Хэширование имени файла и распределение
       файлов по приложениям и далее в разные папки
       по дате"""
    today = date.today().isoformat()
    save_folder = today
    ext = os.path.splitext(filename)[1]
    name = str(instance.pk or '') + filename
    filename = md5(name.encode('utf8')).hexdigest() + ext
    if instance.__class__.__name__ == 'PhotoAdvertisement':
        basedir = 'Advertisement'
    else:
        basedir = instance.__class__.__name__
    return os.path.join(basedir, save_folder, filename)



def add_watermark_to_photo(photo):
    """Добавление водяного знака на изображение"""
    photo = Image.open(photo)
    draw = ImageDraw.Draw(photo)
    width, height = photo.size
    font = ImageFont.truetype("./main_page_domer/static/fonts/arial/arial_bolditalicmt.ttf", int(width / 100 * 6))
    watermark_word = "ДОМер.бел"
    x = width - 10
    y = height - 10
    watermark_text = Image.new("RGBA", photo.size, (255, 255, 255, 0))
    watermark = ImageDraw.Draw(watermark_text)
    watermark.text((x, y), watermark_word, (255, 255, 255, 80), font=font, anchor='rb')
    photo = photo.convert(mode="RGBA")
    photo = Image.alpha_composite(photo, watermark_text)
    return photo


def unique_slugify(instance, slug):
    """ Генератор уникальных SLUG для
        моделей, в случае существования
        такого SLUG."""
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def convert_image_to_avif(photo):
    """ Конвертирует все форматы фото в avif """

    # Открываем загруженный файл с помощью Pillow
    img = Image.open(photo)

    # Создаём временный буфер для сохранения изображения в формате AVIF
    img_io = BytesIO()

    # Сохраняем изображение в формате AVIF
    img.save(img_io, format='AVIF')

    # Перематываем буфер обратно в начало
    img_io.seek(0)

    # Генерируем новое имя файла с расширением .avif
    new_filename = os.path.splitext(photo.name)[0] + '.avif'

    # Обновляем файл в поле photo с новым расширением
    photo.save(new_filename, ContentFile(img_io.read()), save=False)
