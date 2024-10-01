import os
from celery import shared_task
from django.core.files import File
from django.db import transaction
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

    Advertisement.objects.filter(author=user,
                                 id=advertisement_id
                                 ).update(moderated='',
                                          additional_information=additional_information,
                                          **data,
                                          additional_information_view=list(additional_information.items()),
                                          is_active=False)

    advertisement = Advertisement.objects.get(author=user, id=advertisement_id)
    advertisement.save()

    if new_preview_photo_from_old_ones:
        old_preview_image = advertisement.preview_image
        old_photo = PhotoAdvertisement.objects.get(photo=new_preview_photo_from_old_ones,
                                                   advertisement=advertisement).photo

        Advertisement.objects.filter(author=user, id=advertisement_id).update(preview_image=old_photo)
        PhotoAdvertisement.objects.filter(photo=new_preview_photo_from_old_ones,
                                          advertisement=advertisement).update(photo=old_preview_image)
    if processed_photo:
        preview_img = processed_photo.get('preview_img', None)
        other_images = processed_photo.get('other_img', None)
        if preview_img:
            if advertisement.preview_image:
                PhotoAdvertisement.objects.create(photo=advertisement.preview_image, advertisement=advertisement)
            with open(preview_img, 'rb') as f:
                advertisement.preview_image = File(f)
                advertisement.save()
            os.remove(preview_img)
        if other_images:
            for photo in other_images:
                with open(photo, 'rb') as f:
                    additional_photo = PhotoAdvertisement(photo=File(f), advertisement=advertisement)
                    additional_photo.save()
                os.remove(photo)

    if delete_photo:
        PhotoAdvertisement.objects.filter(photo__in=delete_photo, advertisement=advertisement).delete()
        if advertisement.preview_image in delete_photo:
            file_path = advertisement.preview_image.path
            folder_path = os.path.dirname(file_path)
            os.remove(file_path)
            advertisement.preview_image = None
            advertisement.save()

            if not os.listdir(folder_path):  # Если папка пуста
                os.rmdir(folder_path)  # Удаляем папку
