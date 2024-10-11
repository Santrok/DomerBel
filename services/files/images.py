import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def add_watermark_to_image(photo):
    """
    Добавляет водяной знак на изображение
    """
    photo = Image.open(photo)
    draw = ImageDraw.Draw(photo)
    width, height = photo.size
    font = ImageFont.truetype("./main/static/fonts/arial/arial_bolditalicmt.ttf", int(width / 100 * 6))
    watermark_word = "ДОМер.бел"
    x = width - 10
    y = height - 10
    watermark_text = Image.new("RGBA", photo.size, (255, 255, 255, 0))
    watermark = ImageDraw.Draw(watermark_text)
    watermark.text((x, y), watermark_word, (255, 255, 255, 80), font=font, anchor='rb')
    photo = photo.convert(mode="RGBA")
    photo = Image.alpha_composite(photo, watermark_text)
    return photo


def convert_image_to_avif(photo):
    """
    Конвертирует все форматы фото в avif
    """

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
