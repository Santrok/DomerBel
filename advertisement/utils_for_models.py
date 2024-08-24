import random
import os
from datetime import date

from uuid import uuid4
from slugify import slugify
from PIL import Image, ImageDraw, ImageFont
from hashlib import md5

# from .models import Advertisement

def upload_to(instance, filename):
    """Хэширование имени файла и распределение
       файлов по приложениям и далее в разные папки
       случайным образом"""
    # a = Advertisement(id=id)
    # print(instance.advertisement.slug)
    # advertisement_slug = instance.advertisement.slug if instance.advertisement else 'no-slug'
    today = date.today().isoformat()
    # folders = ('folder1', 'folder2', 'folder3')
    # save_folder = random.choice(folders)
    # save_folder = today + '/' + advertisement_slug
    save_folder = today
    ext = os.path.splitext(filename)[1]
    name = str(instance.pk or '') + filename
    filename = md5(name.encode('utf8')).hexdigest() + ext
    basedir = os.path.join(instance._meta.app_label)
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