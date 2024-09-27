import os
from django.core.files.storage import FileSystemStorage
from advertisement.models import Field
from api_domer.serializers import AdditionalInformationSerializer


def validate_additional_information(keys_to_delete, additional_information):
    """ """
    for key in keys_to_delete:
        if key in additional_information:
            del additional_information[key]
    key_error = []
    for i in additional_information:
        if '' in additional_information.get(i):
            key_error.append(i)
    additional_information_filter = Field.objects.filter(id__in=key_error).exclude(error='')
    serializer_additional_error = AdditionalInformationSerializer(data=additional_information_filter, many=True)
    serializer_additional_error.is_valid()
    return serializer_additional_error, additional_information


def save_temp_photo(photo_list, preview_img=None):
    """
    Сохраняет фотографии во временную директорию.
    Возвращает список адресов фотографий.
    Используется для сохранения и редактирования объявлений
    """
    processed_photo = {'preview_img': None, 'other_img': []}

    if photo_list:
        for photo in photo_list:

            # Указываем путь для временного хранения файлов
            temp_dir = os.path.join('media', 'temp')

            # Указываем путь, где будут храниться файлы
            custom_storage = FileSystemStorage(location=temp_dir)

            # Сохраняем файл в указанную директорию
            filename = custom_storage.save(photo.name, photo)

            # Возвращаем полный путь к файлу
            file_path = custom_storage.path(filename)


            if photo.name == preview_img:
                processed_photo['preview_img'] = file_path
            else:
                processed_photo['other_img'].append(file_path)

        return processed_photo
    else:
        return None