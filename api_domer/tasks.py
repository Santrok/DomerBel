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
        other_images = processed_photo.get('other_img')
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

    # if photo_list:
    #     for photo in photo_list:
    #         if photo.name == preview_img:
    #             if advertisement.preview_image not in deleted_images:
    #                 PhotoAdvertisement.objects.create(photo=advertisement.preview_image,
    #                                                   advertisement=advertisement)
    #             advertisement.preview_image = photo
    #             advertisement.save()
    #             preview_img = advertisement.preview_image
    #         else:
    #             additional_photo = PhotoAdvertisement(photo=photo, advertisement=advertisement)
    #             additional_photo.save()

    # if advertisement.preview_image != preview_img:
    #     if advertisement.preview_image not in deleted_images:
    #         PhotoAdvertisement.objects.create(photo=advertisement.preview_image,
    #                                           advertisement=advertisement)
    #     if preview_img:
    #         advertisement.preview_image = preview_img
    #         inst = get_object_or_404(PhotoAdvertisement, photo=preview_img)
    #         PhotoAdvertisement.objects.filter(id=inst.id).update(photo=None)
    #         PhotoAdvertisement.objects.filter(id=inst.id).delete()
    #     else:
    #         advertisement.preview_image = None
    #     advertisement.save()
    #

    if delete_photo != ['']:
        print('удаляю фото')
        PhotoAdvertisement.objects.filter(photo__in=delete_photo, advertisement=advertisement).delete()

    return 'ХУЙ'
