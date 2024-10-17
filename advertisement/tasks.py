import os
import shutil
from distutils.file_util import copy_file

import pytz
import redis
import contextlib

from celery import shared_task
from celery.schedules import crontab
from charset_normalizer.md import getLogger
from django.urls import reverse
from redbeat import RedBeatSchedulerEntry
from django.db import transaction
from django.utils import timezone
from django.core.files import File
from django.db.models import F, Q
from redis.commands.search.reducers import count

from config import settings
from config.celery_app import app
from config.settings import RED_BEAT_REDIS_URL, TIME_ZONE
from services.email.message import run_send_email_task_celery
from related_data.models import Field
from .models import PhotoAdvertisement, Advertisement, Store, UploadFile
from .utils_for_bulk_import import save_many_ads_from_excel, save_many_ads_from_zip

import logging

#Настройка логгирования
logger = logging.getLogger('celery')


def get_current_datetime(timezone_=TIME_ZONE):
    """
    Функция возвращает текущее время в часовом поясе.
    """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone(timezone_)
    datetime_by_timezone = current_datetime.astimezone(timezone_now)
    return datetime_by_timezone


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
    # Добавляем другие изображения
    if other_images:
        for photo in other_images:
            with open(photo, 'rb') as f:
                additional_photo = PhotoAdvertisement(photo=File(f), advertisement=advertisement)
                additional_photo.save()


def delete_photos(advertisement, photos_to_delete):
    """
    Удаляет фотографии.
    """
    PhotoAdvertisement.objects.filter(photo__in=photos_to_delete, advertisement=advertisement).delete()

    if advertisement.preview_image in photos_to_delete:
        file_path = advertisement.preview_image.path
        folder_path = os.path.dirname(file_path)
        
        # Удаляем файл превью и очищаем поле
        if os.path.exists(file_path):
            os.remove(file_path)
        advertisement.preview_image = None
        advertisement.save()

        # Если папка есть и пуста, удаляем её
        if os.path.exists(folder_path) and not os.listdir(folder_path):
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
    Отправка уведомления о создании объявления администрации сайта
    """
    additional_information = update_additional_information(additional_information)

    try:
        with transaction.atomic():
            new_advertisement = Advertisement(author_id=user, additional_information=additional_information, **data)

            if not temporarily_saving_photos:
                new_advertisement.save()
            else:
                preview_img = temporarily_saving_photos.get('preview_img')
                other_images = temporarily_saving_photos.get('other_img', [])
                try:
                    with open(preview_img, 'rb') as f:
                        new_advertisement.preview_image = File(f)
                        new_advertisement.save()
                except Exception as e:
                    logger.error(f'Ошибка при сохранении в объяелвении фото: {str(e)}', exc_info=True)

                if other_images:
                    for photo in other_images:
                        try:
                            with open(photo, 'rb') as f:
                                additional_photo = PhotoAdvertisement(photo=File(f), advertisement=new_advertisement)
                                additional_photo.save()
                        except Exception as e:
                            logger.error(f'Ошибка при сохранении в объяелвении фото: {str(e)}', exc_info=True)
            logger.info(f'Объявление (id:{new_advertisement.id}) успешно сохрано.')

    except Exception as e:
        logger.error(f'Ошибка при сохранении объявления: {str(e)}', exc_info=True)
        run_send_email_task_celery("Ошибка при создании объявления",
                                   "asend_create_advertisement_error.html",
                                   data['email'],
                                   activation_title=data['title'], )
    else:
        run_send_email_task_celery('Новое объявление',
                                   'asend_notification.html',
                                   settings.EMAIL_HOST_USER,
                                   subject="Добавлено новое объявление",
                                   message='Новое объявление требует модерации на сайте Домер.бел',
                                   link=f"{reverse('admin:index')}advertisement/advertisement/{new_advertisement.id}/change/"
                                   )

    if temporarily_saving_photos:
        delete_files(temporarily_saving_photos)


@shared_task()
def update_advertisement_task(user, advertisement_id, data, additional_information, temporarily_saving_photos,
                              new_preview_photo_from_old_ones, delete_photo):
    """
    Редактирует объявление.
    Отправка уведомления о редактировании объявления администрации сайта
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
            else:
                if delete_photo:
                    delete_photos(editing_advertisement, delete_photo)

                if new_preview_photo_from_old_ones:
                    swap_preview_images(editing_advertisement, new_preview_photo_from_old_ones)

                if temporarily_saving_photos:
                    add_new_photos(editing_advertisement, temporarily_saving_photos)
            logger.info(f'Объявления {advertisement_id} успешно обновлено')
    except Exception as e:
        logger.error(f'Ошибка при обновлении объявления (id: {advertisement_id}): {str(e)}', exc_info=True)
    else:
        run_send_email_task_celery('Объявление было изменено',
                                   'asend_notification.html',
                                   settings.EMAIL_HOST_USER,
                                   subject="Объявление изменено",
                                   message=f'Объявление id={advertisement_id} требует модерации на сайте Домер.бел',
                                   link=f"{reverse('admin:index')}advertisement/advertisement/{advertisement_id}/change/",
                                   )

    if temporarily_saving_photos:
        delete_files(temporarily_saving_photos)


@shared_task()
def deactivate_advertisement():
    """ Функция деактивации объявлений по истечению времени публикации """
    current_datetime = get_current_datetime()
    try:
        deactivate_advertisements = Advertisement.objects.filter(date_of_deactivate__lt=current_datetime, is_active=True)
        deactivate_advertisements.update(is_active=False)
        logger.info(f'Деактивировано {deactivate_advertisements.count()} объявлений')
    except Exception as e:
        logger.error(f'Не удалось деактивировать {deactivate_advertisements.count()} объявлений : {str(e)}',
                     exc_info=True)


@shared_task()
def delete_advertisement():
    """ Функция удаления объявлений по истечению времени """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = get_current_datetime()
    try:
        delete_advertisements = Advertisement.objects.filter(date_of_delete__lt=current_datetime, is_active=False)
        count = delete_advertisements.count()
        delete_advertisements.delete()
        logger.info(f'Успешно удалено {count} объявлений')
    except Exception as e:
        logger.error(f'Не удалось удалисть объявления: {str(e)}')



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
            logger.info('Нет объявлений для ротации')
            return
        try:
            update_vip_advertisements(all_ads_vip, 'shown_vip', 'shown_vip_count')
            logger.info(f'Ротацию прошли {all_ads_vip.count()} объявлений')
        except Exception as e:
            logger.error(f'Ротация VIP объявлений не прошла: {str(e)}', exc_info=True)

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
            logger.info('Нет VIP-объявлений')
            return

        for category in categories:
            try:
                ads_by_category = Advertisement.objects.filter(category=category, moderated=True, is_active=True, vip=True)
                update_vip_advertisements(ads_by_category,
                                          'shown_vip_category',
                                          'shown_vip_category_count')
                logger.info(f'Успешно выполнена ротация для VIP-объявлений категоририи: {category}')
            except Exception as e:
                logger.error(f'Ротация по категории {category} выполнена неудачно: {str(e)}', exc_info=True)


@shared_task()
def deactivate_store():
    """
    Функция деактивации магазина по истечению времени публикации.
    """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = get_current_datetime()
    try:
        deactivate_stores = Store.objects.filter(date_of_deactivate__lt=current_datetime, is_active=True)
        deactivate_stores.update(is_active=False)
        logger.info(f'Текущее время {current_datetime}, деактивировано {deactivate_stores.count()}')
    except Exception as e:
        logger.error(f"Деактиваия магазинов по истечению времени выполнено неудачно: {str(e)}", exc_info=True)


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
def save_many_ads_from_excel_task(upload_file, id, first_name, phone_number, email):
    """
    Сохраняет объявления из экселя.
    """
    try:
        result = save_many_ads_from_excel(upload_file, id, first_name, phone_number, email)
        if result is True:
            logger.info(f'Пользователем {email} загружен файл {upload_file}. Все объявления сохранены успешно')
        else:
            logger.info(f'Пользователем {email} загружен файл {upload_file}. Сформирован файл с ошибками: {result.get("file")}')
        return result
    except Exception as e:
        logger.error(f'Неудалось обраборать файл {upload_file} для массовго импорта объявлений от польователя {email}: {str(e)}',
                     exc_info=True)


@shared_task()
def save_many_ads_from_zip_task(upload_zip, id, first_name, phone_number, email):
    """
    Сохраняет объявления из zip-архива.
    """
    try:
        result = save_many_ads_from_zip(upload_zip, id, first_name, phone_number, email)
        if result is True:
            logger.info(f'Пользователем {email} загружен файл {upload_zip}. Все объявления сохранены успешно')
        else:
            logger.info(f'Пользователем {email} загружен файл {upload_zip}. Сформирован файл с ошибками: {result.get("file")}')
        return result
    except Exception as e:
        logger.error(
            f'Неудалось обраборать файл {upload_zip} для массовго импорта объявлений от польователя {email}: {str(e)}',
            exc_info=True)


@shared_task()
def delete_upload_file_beat():
    """
    Удаляет все экземпляры модели UoloadFile раз в сутки.
    """
    files = UploadFile.objects.filter(status=True)
    count = files.count()
    try:
        files.delete()
        logger.info(f'Удалено {count} загруженных файлов для массового импорта объявлений')
    except Exception as e:
        logger.warning(f'Не удалось удалить несколько файлов: {str(e)}', exc_info=True)


def create_tasks_from_schedule(name, task, schedule_, args=None, kwargs=None):
    """
    Функция добавляет периодическую задачи в celery.
    """
    entry = RedBeatSchedulerEntry(
        name=name,
        task=task,
        schedule=schedule_,
        args=args or [],
        kwargs=kwargs or {},
        app=app
    )
    entry.save()


def delete_task(task_id):
    """
    Функция удаляет периодическую задачи в celery.
    """
    try:
        entry = RedBeatSchedulerEntry.from_key(task_id, app=app)
        if entry:
            try:
                entry.delete()  # Пробуем удалить
                logger.info(f"Задача {task_id} успешно удалена.")
            except Exception as e:
                logger.error(f"Ошибка при удалении задачи: {str(e)}", exc_info=True)
    except KeyError:
        logger.error(f"Задача {task_id} не найдена.", exc_info=True)


def get_list_tasks():
    """
    Функция получает все периодические задачи который
    сейчас загружены в redis.
    """
    r = redis.StrictRedis.from_url(RED_BEAT_REDIS_URL)

    # Получаем все ключи RedBeat с префиксом 'redbeat:'
    tasks = r.keys('redbeat:*')
    list_tasks = []

    # Декодируем каждый ключ из байтового формата в строковый формат
    for task in tasks:
        task_name = task.decode('utf-8')
        if task_name.startswith('redbeat:') and '::' not in task_name:
            list_tasks.append(task_name)

    return list_tasks


@shared_task()
def deactivation_of_paid_services(ads_id, name_for_delete, **fild_update):
    """
    Функция отключает выбранную платную услугу и удаляет эту
    задачу из redbeat:schedule.
    """
    Advertisement.objects.filter(id=ads_id).update(**fild_update)
    try:
        delete_task(name_for_delete)
        logger.info(f'Объявлениe (id: {ads_id}) обновлено с параметрами: {fild_update}. Задача {name_for_delete} успешно удалена')
    except Exception as e:
        logger.error(f'Не удалось удлить задачу: {str(e)}')


@shared_task()
def raise_or_deactivation_of_paid_services(ads_id, name_for_delete, **fild_update):
    """
    Функция поднимает объявления в поиске,
    также отключает платную услугу поднять в поиске и удаляет
    эту задачу из redbeat:schedule.
    """
    current_datetime = get_current_datetime()
    try:
        ads = Advertisement.objects.filter(id=ads_id)
        ads.update(search_boost_date=current_datetime)
        logger.info(f'Объявление (id: {ads_id}) обнoвлено с датой поднятия в поиске {current_datetime}')
        if ads.first().date_of_deactivate_special_accommodation.date() == current_datetime.date():
            deactivation_of_paid_services(ads_id, name_for_delete, **fild_update)
    except Exception as e:
        logger.error(f'Не удалось поднять обявление (id: {ads_id} в поиске: {str(e)}', exc_info=True)


@shared_task()
def update_schedule():
    """
    Функция динамического обновления redbeat:schedule.
    """
    current_datetime = get_current_datetime()
    advertisements_for_deactivate = Advertisement.objects.filter(is_active=True).filter(
        Q(date_of_deactivate_vip__date__lte=current_datetime.date(), vip=True) |
        Q(date_of_deactivate_highlight_ad__date__lte=current_datetime.date(), highlight_ad=True) |
        Q(special_accommodation=True))

    if not advertisements_for_deactivate:
        logger.info(f'Текущее время: {current_datetime}. Объявлений для деактивации не найдено.')
        return

    for ads in advertisements_for_deactivate:
        if ads.vip and ads.date_of_deactivate_vip.date() <= current_datetime.date():
            name = f'deactivate_advertisement_vip_{ads.id}'
            schedule_ = crontab(hour=ads.date_of_deactivate_vip.hour + 3, minute=ads.date_of_deactivate_vip.minute)

            if ads.date_of_deactivate_vip < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour, minute=current_datetime.minute + 1)
            try:
                create_tasks_from_schedule(name,
                                           "advertisement.tasks.deactivation_of_paid_services",
                                           schedule_,
                                           [ads.id, f'redbeat:{name}'],
                                           {'vip': False})
                logger.info(f'Запланировано в объявлении (id: {ads.id}) отключить платные услуги. Имя задачи: {name}.')
            except Exception as e:
                logger.error(f'Не удалось заплонировать отключить платные услуги в объявлении (id: {ads.id}): {str(e)}',
                             exc_info=True)


        if ads.highlight_ad and ads.date_of_deactivate_highlight_ad <= current_datetime:
            name = f'deactivate_advertisement_highlight{ads.id}'
            schedule_ = crontab(hour=ads.date_of_deactivate_highlight_ad.hour + 3,
                                minute=ads.date_of_deactivate_highlight_ad.minute)

            if ads.date_of_deactivate_highlight_ad < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour, minute=current_datetime.minute + 1)
            try:
                create_tasks_from_schedule(name,
                                           "advertisement.tasks.deactivation_of_paid_services",
                                           schedule_,
                                           [ads.id, f'redbeat:{name}'],
                                           {'highlight_ad': False})
                logger.info(f'Запланирована деактивация выделения объявления (id: {ads.id}). Имя задачи: {name}.')
            except Exception as e:
                logger.error(f'Не удалось запланировать деактивацию объявления (id: {ads.id}): {str(e)}',
                             exc_info=True)

        if ads.date_of_deactivate_special_accommodation:
            name = f'raise_or_deactivate_advertisement_special_accommodation_{ads.id}'
            schedule_ = crontab(hour=ads.date_of_deactivate_special_accommodation.hour + 3,
                                minute=ads.date_of_deactivate_special_accommodation.minute)
            task = "advertisement.tasks.raise_or_deactivation_of_paid_services"

            if ads.date_of_deactivate_special_accommodation < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour, minute=current_datetime.minute + 1)
                task = "advertisement.tasks.deactivation_of_paid_services"
            try:
                create_tasks_from_schedule(name,
                                           task,
                                           schedule_,
                                           [ads.id, f'redbeat:{name}'],
                                           {'special_accommodation': False})
                logger.info(f'Запланировано деактивация специального размещения объявления (id: {ads.id}). Имя задачи: {name}.')
            except Exception as e:
                logger.error(f'Не удалось запланировать деактивацию для пециального размещения для объявления (id: {ads.id}): {str(e)}',
                             exc_info=True)

