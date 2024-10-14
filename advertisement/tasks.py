import contextlib
import os
import shutil
from datetime import timezone, timedelta

import pytz
from celery import shared_task
from celery.schedules import crontab
from django.core.files import File
from django.db import transaction

from config.celery_app import app
from django.db.models import F

from related_data.models import Field
from services.email.message import run_send_email_task_celery
from .models import PhotoAdvertisement, Advertisement, ErrorFile
from .utils_for_bulk_import import save_many_ads_from_excel, save_many_ads_from_zip


def update_additional_information(additional_information):
    """
    Обновляет дополнительную информацию для объявления.
    """
    fields = Field.objects.filter(id__in=additional_information).order_by('id')
    for field in fields:
        additional_information[field.title] = ', '.join(additional_information.pop(f'{field.id}'))
    return additional_information


def swap_preview_images(advertisement, new_preview_photo):
    """
    Меняет местами главное изображение с другим.
    """
    old_preview_image = advertisement.preview_image
    old_photo = PhotoAdvertisement.objects.get(photo=new_preview_photo, advertisement=advertisement)

    # Меняем изображения
    advertisement.preview_image = old_photo.photo
    advertisement.save()

    old_photo.photo = old_preview_image
    old_photo.save()


def add_new_photos(advertisement, temporarily_saving_photos):
    """
    Добавляет новые фотографии к объявлению.
    """
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
        # files_to_delete.append(preview_img)
    # Добавляем другие изображения
    if other_images:
        for photo in other_images:
            with open(photo, 'rb') as f:
                additional_photo = PhotoAdvertisement(photo=File(f), advertisement=advertisement)
                additional_photo.save()
            # files_to_delete.append(photo)


def delete_photos(advertisement, photos_to_delete):
    """
    Удаляет фотографии.
    """
    PhotoAdvertisement.objects.filter(photo__in=photos_to_delete, advertisement=advertisement).delete()

    if advertisement.preview_image in photos_to_delete:
        file_path = advertisement.preview_image.path
        folder_path = os.path.dirname(file_path)

        # Удаляем файл превью и очищаем поле
        os.remove(file_path)
        advertisement.preview_image = None
        advertisement.save()

        # Если папка пуста, удаляем её
        if not os.listdir(folder_path):
            os.rmdir(folder_path)


def remove_file(file_path):
    """
    Удаляет файл, если он существует, и выводит сообщение об ошибке в случае неудачи.
    """
    with contextlib.suppress(OSError):
        os.remove(file_path)


def delete_files(temporarily_saving_photos):
    """
    Удаляет временные файлы и пустые папки.
    """
    preview_img = temporarily_saving_photos.get('preview_img')
    other_images = temporarily_saving_photos.get('other_img', [])

    folder_path = None

    if preview_img:
        folder_path = os.path.dirname(preview_img)
        remove_file(preview_img)

    if other_images:
        folder_path = os.path.dirname(other_images[0])
        for photo in other_images:
            remove_file(photo)

    # Удаляем папку, если она пуста
    if folder_path and not os.listdir(folder_path):
        with contextlib.suppress(OSError):
            os.rmdir(folder_path)


@shared_task()
def save_advertisement_task(user, data, additional_information, temporarily_saving_photos):
    """
    Сохраняет объявление.
    """
    additional_information = update_additional_information(additional_information)

    try:
        with transaction.atomic():
            new_advertisement = Advertisement(author_id=user, additional_information=additional_information, **data)

            if not temporarily_saving_photos:
                new_advertisement.save()
                return

            preview_img = temporarily_saving_photos.get('preview_img')
            other_images = temporarily_saving_photos.get('other_img', [])
            with open(preview_img, 'rb') as f:
                new_advertisement.preview_image = File(f)
                new_advertisement.save()

            if other_images:
                for photo in other_images:
                    with open(photo, 'rb') as f:
                        additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                        additional_photo.save()

    except Exception as e:
        run_send_email_task_celery("Ошибка при создании объявления",
                                   "asend_create_advertisement_error.html",
                                   data['email'],
                                   activation_title=data['title'],)
        print(e)

    if temporarily_saving_photos:
        delete_files(temporarily_saving_photos)


@shared_task()
def update_advertisement_task(user, advertisement_id, data, additional_information, temporarily_saving_photos,
                              new_preview_photo_from_old_ones, delete_photo):
    """
    Редактирует объявление.
    """
    additional_information = update_additional_information(additional_information)

    editing_advertisement = Advertisement.objects.get(author=user, id=advertisement_id)
    data['moderated'] = None
    data['additional_information'] = additional_information
    data['is_active'] = False

    # Обновляем поля объявления
    for key, value in data.items():
        setattr(editing_advertisement, key, value)

    try:
        with transaction.atomic():
            if not new_preview_photo_from_old_ones and not temporarily_saving_photos and not delete_photo:
                editing_advertisement.save()
                return

            if new_preview_photo_from_old_ones:
                swap_preview_images(editing_advertisement, new_preview_photo_from_old_ones)

            if temporarily_saving_photos:
                add_new_photos(editing_advertisement, temporarily_saving_photos)

            if delete_photo:
                delete_photos(editing_advertisement, delete_photo)

    except Exception as e:
        print(f"Ошибка при обновлении объявления: {e}")

    if temporarily_saving_photos:
        delete_files(temporarily_saving_photos)


@shared_task()
def deactivate_advertisement():
    """
    Функция деактивации объявлений по истечению времени публикации
    """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)

    deactivate_advertisements = Advertisement.objects.filter(date_of_deactivate__lt=aware_datetime, is_active=True)
    deactivate_advertisements.update(is_active=False)


@shared_task()
def delete_advertisement():
    """
    Функция удаления объявлений по истечению времени
    """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)

    delete_advertisements = Advertisement.objects.filter(date_of_delete__lt=aware_datetime, is_active=False)
    delete_advertisements.delete()


def reset_shown_count(ad_filter, field, min_shown_count, max_shown_number):
    """
    Сбрасывает счетчик показов для объявлений.
    """
    if min_shown_count > max_shown_number:
        ad_filter.update(**{field: 0})


def update_vip_advertisements(ad_filter, field_shown, field_count):
    """
    Обновляет показанные VIP объявления на основе минимальных показов.
    """
    total_count = ad_filter.count()
    total_shown_count = ad_filter.filter(**{field_shown: True}).count()
    first_ad = ad_filter.order_by(field_count).first()
    min_shown_count = getattr(first_ad, field_count)

    reset_shown_count(ad_filter, field_count, min_shown_count, 10)

    if 3 >= total_count != total_shown_count:
        ad_filter.update(**{field_shown: True})
        return

    if total_count > 3:
        ad_filter.update(**{field_shown: False})
        ads_to_show = ad_filter.filter(**{field_count: min_shown_count})[:3]

        if ads_to_show.count() < 3:
            remaining_ads = ad_filter.exclude(id__in=ads_to_show).order_by(field_count)[:3 - ads_to_show.count()]
            ads_to_show = ads_to_show.union(remaining_ads)

        ad_filter.filter(id__in=[ad.id for ad in ads_to_show]).update(
            **{field_shown: True, field_count: F(field_count) + 1}
        )


@shared_task()
def list_shown_vip():
    """
    Ротация VIP объявлений.
    """
    with transaction.atomic():
        all_ads_vip = Advertisement.objects.filter(moderated=True, is_active=True, vip=True)
        if not all_ads_vip.exists():
            return

        update_vip_advertisements(all_ads_vip, 'shown_vip', 'shown_vip_count')


@shared_task()
def list_shown_vip_category():
    """
    Ротация VIP объявлений по категориям.
    """
    with transaction.atomic():
        categories = Advertisement.objects.filter(moderated=True,
                                                  is_active=True,
                                                  vip=True).values_list('category', flat=True).distinct('category')
        if not categories.exists():
            print('No VIP ads')
            return

        for category in categories:
            ads_by_category = Advertisement.objects.filter(category=category, moderated=True, is_active=True, vip=True)
            update_vip_advertisements(ads_by_category,
                                      'shown_vip_category',
                                      'shown_vip_category_count')


@shared_task()
def delete_everything_in_folder_beat():
    """
    Удаляет все файлы из папки для "files_for_bulk_import_of_ads"
    Задача отрабатывает раз в сутки в 00.00
    """
    path = './media/files_for_bulk_import_of_ads'
    shutil.rmtree(path)
    os.mkdir(path)


@shared_task()
def save_many_ads_from_excel_task(uploud_file, id, first_name, phone_number, email):
    """
    Сохраняет объявления из экселя
    """
    result = save_many_ads_from_excel(uploud_file, id, first_name, phone_number, email)
    return result


@shared_task()
def save_many_ads_from_zip_task(uploud_zip, id, first_name, phone_number, email):
    """
    Cохраняет объявления из zip-архива
    """
    result = save_many_ads_from_zip(uploud_zip, id, first_name, phone_number, email)
    return result


@shared_task()
def delete_error_file_beat():
    """
    Удаляет все экземпляры модели ErrorFile раз в сутки
    """
    files = ErrorFile.objects.all()
    files.delete()


@shared_task()
def deactivate_advertisement():
    print("Все сработало как надо")


# @shared_task()
def update_schedule(data):
    """
    Функция обновляет задачи Celery согласно времени деактивации платных функций
    """

    print('-----------------------------------------')
    print(app.conf.beat_schedule)
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)


    list_advertisements_for_deactivate = Advertisement.objects.filter(search_boost_date__date=aware_datetime.date(),
                                                                      is_active=True)
    # print(list_advertisements_for_deactivate)
    print('++++++++++++++++++++++++++++++++')
    #
    # for i in list_advertisements_for_deactivate:
    #     print(i.search_boost_date.astimezone(timezone_now), i.search_boost_date.hour, i.search_boost_date.minute)

    # Удаляем только задачи, относящиеся к `ads_deactivate_`
    for task_name in list(app.conf.beat_schedule.keys()):
        if task_name.startswith("ads_deactivate_"):
            del app.conf.beat_schedule[task_name]

    # if not list_advertisements_for_deactivate:
    #     print('stop')
    #     return

    for i in list_advertisements_for_deactivate:
        task_name = f'ads_deactivate_{i.id}'
        app.conf.beat_schedule[task_name] = {
                "task": "advertisement.tasks.deactivate_advertisement",
                "schedule": crontab(hour=i.search_boost_date.hour+3, minute=i.search_boost_date.minute),
        }

    app.conf.beat_schedule['list_shown_vip'] = {
        "task": "advertisement.tasks.list_shown_vip",
        "schedule": timedelta(seconds=5),
    }

    # app.control.reload_task('list_shown_vip')
    app.control.pool_restart()

    app.conf.beat_schedule['111111'] = {
        "task": "advertisement.tasks.deactivate_advertisement",
        "schedule": timedelta(seconds=5)
    }

    # app.control.broadcast('pool_restart', arguments={'reload': True})
    # current_app.Beat().scheduler.update(current_app.conf.beat_schedule)

    # print("!!!", app.control.inspect().registered())
    print(app.conf.beat_schedule)
    print('-----------------------------------------')

