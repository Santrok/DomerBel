import os
from PIL import Image
import pillow_avif

def convert_jpg_to_avif(source_folder, destination_folder):
    """
    Конвертирует все JPG файлы в указанной папке в формат AVIF и сохраняет их в другой папке.

    Args:
        source_folder: Путь к исходной папке с JPG файлами.
        destination_folder: Путь к папке для сохранения AVIF файлов.
    """

    for i in range(1, 101):
        source_path = os.path.join(source_folder, str(i))
        destination_path = os.path.join(destination_folder, str(i))

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        for filename in os.listdir(source_path):
            if filename.endswith(".jpg"):
                img_path = os.path.join(source_path, filename)
                avif_path = os.path.join(destination_path, filename[:-4] + ".avif")

                # Открываем изображение с помощью Pillow
                img = Image.open(img_path)

                # Сохраняем изображение в формате AVIF
                img.save(avif_path, format="AVIF")

def convert_jpg_to_avif_for_store(source_folder, destination_folder):
    """
    Конвертирует все JPG файлы в указанной папке в формат AVIF и сохраняет их в другой папке.

    Args:
        source_folder: Путь к исходной папке с JPG файлами.
        destination_folder: Путь к папке для сохранения AVIF файлов.
    """

    for filename in os.listdir(source_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(source_folder, filename)
            avif_path = os.path.join(destination_folder, filename[:-4] + ".avif")

            # Открываем изображение с помощью Pillow
            img = Image.open(img_path)

            # Сохраняем изображение в формате AVIF
            img.save(avif_path, format="AVIF")

# Пример использования
source_folder = "/home/nemo/Документы/Prod/DomerBelNew/media/foto"
source_folder_for_store = "/home/nemo/Документы/Prod/DomerBelNew/media/images/store_img1"
destination_folder = "foto1"
destination_folder_for_store = "/home/nemo/Документы/Prod/DomerBelNew/media/images/store_img"

convert_jpg_to_avif(source_folder, destination_folder)
convert_jpg_to_avif_for_store(source_folder_for_store, destination_folder_for_store)
