import os
from celery import shared_task
from django.core.files import File
from django.shortcuts import get_object_or_404

from advertisement.models import Field, PhotoAdvertisement, Advertisement


@shared_task()
def save_advertisement_task(user, data, additional_information, processed_photo):
    """ Сохранение объявлений """
    additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')

    for i in additional_information_save:
        additional_information[i.title] = ', '.join(additional_information.pop(f'{i.id}'))
    new_advertisement = Advertisement(author_id=user,
                                      additional_information=additional_information,
                                      **data)
    new_advertisement.save()

    if processed_photo:
        preview_img = processed_photo.get('preview_img')
        other_images = processed_photo.get('other_img', None)
        with open(preview_img, 'rb') as f:
            new_advertisement.preview_image = File(f)
            new_advertisement.save()
        os.remove(preview_img)
        if other_images:
            for photo in other_images:
                with open(photo, 'rb') as f:
                    additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                    additional_photo.save()
                os.remove(photo)


@shared_task()
def update_advertisement_task(user, advertisement_id, data, additional_information, processed_photo,
                              new_preview_photo_from_old_ones, delete_photo):
    """ Редактирование объявлений """
    additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')
    for i in additional_information_save:
        additional_information[i.title] = ', '.join(additional_information.pop(f'{i.id}'))

    Advertisement.objects.filter(author=user, id=advertisement_id
                                 ).update(moderated=False, additional_information=additional_information,
                                          **data, is_active=False)
    advertisement = Advertisement.objects.get(author=user, id=advertisement_id)

    if new_preview_photo_from_old_ones:
        print('меняю главное фото')
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

    if delete_photo != ['']:
        print('удаляю фото', delete_photo)
        PhotoAdvertisement.objects.filter(photo__in=delete_photo, advertisement=advertisement).delete()
        if advertisement.preview_image in delete_photo:
            os.remove(advertisement.preview_image.path)
            advertisement.preview_image = None
            advertisement.save()
