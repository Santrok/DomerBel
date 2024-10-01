import os
from celery import shared_task
from django.core.files import File
from django.db import transaction
from django.forms import model_to_dict
from django.template.loader import render_to_string

from advertisement.models import Field, PhotoAdvertisement, Advertisement
from config.settings import env_keys
from users.tasks import send_email_task


@shared_task()
def save_advertisement_task(user, data, additional_information, processed_photo):
    """ Сохранение объявлений """
    additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')

    for field in additional_information_save:
        additional_information[field.title] = ', '.join(additional_information.pop(f'{field.id}'))

    try:
        with transaction.atomic():
            new_advertisement = Advertisement(author_id=user, additional_information=additional_information, **data)

            if not processed_photo:
                new_advertisement.save()
                return

            preview_img = processed_photo.get('preview_img')
            other_images = processed_photo.get('other_img', None)
            with open(preview_img, 'rb') as f:
                new_advertisement.preview_image = File(f)
                new_advertisement.save()
            os.remove(preview_img)
            folder_path = os.path.dirname(preview_img)  # Получаем путь к папке, в которой был файл

            if other_images:
                for photo in other_images:
                    with open(photo, 'rb') as f:
                        additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                        additional_photo.save()
                    os.remove(photo)
                folder_path = os.path.dirname(other_images[0])  # Получаем путь к папке, в которой был файл

            if not os.listdir(folder_path):  # Если папка пуста
                os.rmdir(folder_path)  # Удаляем папку

    except Exception as e:
        if processed_photo:
            preview_img = processed_photo.get('preview_img')
            other_images = processed_photo.get('other_img', None)
            os.remove(preview_img)
            folder_path = os.path.dirname(preview_img)  # Получаем путь к папке, в которой был файл
            if other_images:
                for photo in other_images:
                    os.remove(photo)
                folder_path = os.path.dirname(other_images[0])  # Получаем путь к папке, в которой был файл

            if not os.listdir(folder_path):  # Если папка пуста
                os.rmdir(folder_path)  # Удаляем папку

        # !!! Переписать на новую функцию отправки писем!!!
        html_content = render_to_string(
            "asend_create_advertisement_error.html",
            context={"activation_title": data['title'], "url": env_keys.get("URL")},
        )
        send_email_task(chat_title='Ошибка при создании обьявления',
                        recipient=data['email'],
                        text_content=html_content,
                        html_content=html_content)


@shared_task()
def update_advertisement_task(user, advertisement_id, data, additional_information, processed_photo,
                              new_preview_photo_from_old_ones, delete_photo):
    """ Редактирование объявлений """
    additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')

    for field in additional_information_save:
        additional_information[field.title] = ', '.join(additional_information.pop(f'{field.id}'))

    editing_advertisement = Advertisement.objects.get(author=user, id=advertisement_id)

    data['moderated'] = ''
    data['additional_information'] = additional_information
    data['is_active'] = False

    for key, value in data.items():
        setattr(editing_advertisement, key, value)

    if not new_preview_photo_from_old_ones and not processed_photo and not delete_photo:
        editing_advertisement.save()
        return

    if new_preview_photo_from_old_ones:
        print('Меняем две фотки местами')
        old_preview_image = editing_advertisement.preview_image
        old_photo = PhotoAdvertisement.objects.get(photo=new_preview_photo_from_old_ones,
                                                   advertisement=editing_advertisement)

        editing_advertisement.preview_image = old_photo.photo
        editing_advertisement.save()

        old_photo.photo = old_preview_image
        old_photo.save()

    if processed_photo:
        print('Добавляем новые фотки и можем поменять местами')
        preview_img = processed_photo.get('preview_img')
        other_images = processed_photo.get('other_img', None)
        if preview_img:
            if editing_advertisement.preview_image:
                PhotoAdvertisement.objects.create(photo=editing_advertisement.preview_image,
                                                  advertisement=editing_advertisement)
            with open(preview_img, 'rb') as f:
                editing_advertisement.preview_image = File(f)
                editing_advertisement.save()
            os.remove(preview_img)
        if other_images:
            for photo in other_images:
                with open(photo, 'rb') as f:
                    additional_photo = PhotoAdvertisement(photo=File(f), advertisement=editing_advertisement)
                    additional_photo.save()
                os.remove(photo)

    if delete_photo:
        print('Удаляем фотки')
        PhotoAdvertisement.objects.filter(photo__in=delete_photo, advertisement=editing_advertisement).delete()
        if editing_advertisement.preview_image in delete_photo:
            file_path = editing_advertisement.preview_image.path
            folder_path = os.path.dirname(file_path)
            os.remove(file_path)
            editing_advertisement.preview_image = None
            editing_advertisement.save()

            if not os.listdir(folder_path):  # Если папка пуста
                os.rmdir(folder_path)  # Удаляем папку
