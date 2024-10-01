import os
from celery import shared_task
from django.core.files import File
from django.db import transaction
from django.template.loader import render_to_string

from advertisement.models import Field, PhotoAdvertisement, Advertisement
from config.settings import env_keys
from users.tasks import send_email_task


def update_additional_information(additional_information):
    """Обновляем дополнительную информацию для объявления."""
    fields = Field.objects.filter(id__in=additional_information).order_by('id')
    for field in fields:
        additional_information[field.title] = ', '.join(additional_information.pop(f'{field.id}'))
    return additional_information


def swap_preview_images(advertisement, new_preview_photo):
    """Меняем местами главное изображение с другим."""
    old_preview_image = advertisement.preview_image
    old_photo = PhotoAdvertisement.objects.get(photo=new_preview_photo, advertisement=advertisement)

    # Меняем изображения
    advertisement.preview_image = old_photo.photo
    advertisement.save()

    old_photo.photo = old_preview_image
    old_photo.save()


def add_new_photos(advertisement, temporarily_saving_photos, files_to_delete):
    """Добавляем новые фотографии к объявлению."""
    preview_img = temporarily_saving_photos.get('preview_img')
    other_images = temporarily_saving_photos.get('other_img', None)

    if preview_img:
        # Сохраняем старое превью как дополнительное фото
        if advertisement.preview_image:
            PhotoAdvertisement.objects.create(photo=advertisement.preview_image, advertisement=advertisement)

        # Обновляем превью с новой фотографией
        with open(preview_img, 'rb') as f:
            advertisement.preview_image = File(f)
            advertisement.save()
        files_to_delete.append(preview_img)

    # Добавляем другие изображения
    if other_images:
        for photo in other_images:
            with open(photo, 'rb') as f:
                additional_photo = PhotoAdvertisement(photo=File(f), advertisement=advertisement)
                additional_photo.save()  # Сохраняем каждую фотографию по отдельности
            files_to_delete.append(photo)


def delete_photos(advertisement, photos_to_delete, files_to_delete):
    """Удаляем фотографии."""
    PhotoAdvertisement.objects.filter(photo__in=photos_to_delete, advertisement=advertisement).delete()

    if advertisement.preview_image in photos_to_delete:
        file_path = advertisement.preview_image.path
        # folder_path = os.path.dirname(file_path)

        # Удаляем файл превью и очищаем поле
        files_to_delete.append(file_path)
        advertisement.preview_image = None
        advertisement.save()

        # # Если папка пуста, удаляем её
        # if not os.listdir(folder_path):
        #     os.rmdir(folder_path)


def delete_files(files_to_delete):
    """Удаляем временные файлы."""
    print(f'files_to_delete: {files_to_delete}')
    folder_path = os.path.dirname(files_to_delete[0])
    for file in files_to_delete:
        try:
            os.remove(file)
        except OSError as e:
            print(f"Ошибка при удалении файла {file}: {e}")
    if not os.listdir(folder_path):  # Если папка пуста
        os.rmdir(folder_path)  # Удаляем папку


@shared_task()
def save_advertisement_task(user, data, additional_information, temporarily_saving_photos):
    """ Сохранение объявлений """
    additional_information = update_additional_information(additional_information)

    files_to_delete = []  # Создаем список для хранения файлов, которые нужно удалить

    try:
        with transaction.atomic():
            new_advertisement = Advertisement(author_id=user, additional_information=additional_information, **data)

            if not temporarily_saving_photos:
                new_advertisement.save()
                return

            preview_img = temporarily_saving_photos.get('preview_img')
            other_images = temporarily_saving_photos.get('other_img', None)
            with open(preview_img, 'rb') as f:
                new_advertisement.preview_image = File(f)
                new_advertisement.save()
            files_to_delete.append(preview_img)
            # os.remove(preview_img)
            # folder_path = os.path.dirname(preview_img)  # Получаем путь к папке, в которой был файл

            if other_images:
                photos_to_save = []
                for photo in other_images:
                    with open(photo, 'rb') as f:
                        additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                        additional_photo.save()  # Сохраняем каждую фотографию по отдельности
                        # additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                        # photos_to_save.append(additional_photo)
                    files_to_delete.append(photo)
                    # os.remove(photo)
                # PhotoAdvertisement.objects.bulk_create(photos_to_save)
                # folder_path = os.path.dirname(other_images[0])  # Получаем путь к папке, в которой был файл

            # if not os.listdir(folder_path):  # Если папка пуста
            #     os.rmdir(folder_path)  # Удаляем папку

    except Exception as e:
        if temporarily_saving_photos:
            preview_img = temporarily_saving_photos.get('preview_img')
            other_images = temporarily_saving_photos.get('other_img', None)
            files_to_delete.append(preview_img)
            # os.remove(preview_img)
            # folder_path = os.path.dirname(preview_img)  # Получаем путь к папке, в которой был файл
            if other_images:
                for photo in other_images:
                    files_to_delete.append(photo)
                    # os.remove(photo)
                # folder_path = os.path.dirname(other_images[0])  # Получаем путь к папке, в которой был файл

            # if not os.listdir(folder_path):  # Если папка пуста
            #     os.rmdir(folder_path)  # Удаляем папку

        # !!! Переписать на новую функцию отправки писем!!!
        html_content = render_to_string(
            "asend_create_advertisement_error.html",
            context={"activation_title": data['title'], "url": env_keys.get("URL")},
        )
        send_email_task(chat_title='Ошибка при создании обьявления',
                        recipient=data['email'],
                        text_content=html_content,
                        html_content=html_content)

    if files_to_delete:
        # Удаляем все файлы из списка
        delete_files(files_to_delete)

@shared_task()
def update_advertisement_task(user, advertisement_id, data, additional_information, temporarily_saving_photos,
                              new_preview_photo_from_old_ones, delete_photo):
    """Редактирование объявления."""
    additional_information = update_additional_information(additional_information)

    editing_advertisement = Advertisement.objects.get(author=user, id=advertisement_id)
    data['moderated'] = ''
    data['additional_information'] = additional_information
    data['is_active'] = False

    # Обновляем поля объявления
    for key, value in data.items():
        setattr(editing_advertisement, key, value)

    files_to_delete = []  # Создаем список для хранения файлов, которые нужно удалить

    try:
        with transaction.atomic():
            if not new_preview_photo_from_old_ones and not temporarily_saving_photos and not delete_photo:
                editing_advertisement.save()
                return

            if new_preview_photo_from_old_ones:
                print('Меняем две фотки местами')
                swap_preview_images(editing_advertisement, new_preview_photo_from_old_ones)

            if temporarily_saving_photos:
                print('Добавляем новые фотки и можем поменять местами')
                add_new_photos(editing_advertisement, temporarily_saving_photos, files_to_delete)

            if delete_photo:
                print('Удаляем фотки')
                delete_photos(editing_advertisement, delete_photo, files_to_delete)

    except Exception as e:
        print(f"Ошибка при обновлении объявления: {e}")

    if files_to_delete:
        # Удаляем все файлы из списка
        delete_files(files_to_delete)
