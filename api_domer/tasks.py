import os
from celery import shared_task
from django.core.files import File

from advertisement.models import Field, PhotoAdvertisement, Advertisement


@shared_task()
def save_advertisement_task(user, serializer_validated_data, additional_information, processed_photo):
    additional_information_save = Field.objects.filter(id__in=additional_information).order_by('id')

    for i in additional_information_save:
        additional_information[i.title] = ', '.join(additional_information.pop(f'{i.id}'))
    new_advertisement = Advertisement(author_id=user,
                                      additional_information=additional_information,
                                      **serializer_validated_data)
    new_advertisement.save()
    if processed_photo:
        preview_img = processed_photo.get('preview_img')
        other_images = processed_photo.get('other_images')
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