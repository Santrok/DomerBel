import os
import shutil
import pytz
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.db.models import F
from advertisement.models import Advertisement, Store
from advertisement.functions_for_bulk_import import save_many_ads_from_excel, \
    save_many_ads_from_zip
from advertisement.models import ErrorFile


@shared_task()
def deactivate_advertisement():
    """ Функция деактивации объявлений по истечению времени публикации """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)

    deactivate_advertisements = Advertisement.objects.filter(date_of_deactivate__lt=aware_datetime, is_active=True)
    deactivate_advertisements.update(is_active=False)


@shared_task()
def delete_advertisement():
    """ Функция удаления объявлений по истечению времени """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)

    delete_advertisements = Advertisement.objects.filter(date_of_delete__lt=aware_datetime, is_active=False)
    delete_advertisements.delete()


def reset_shown_count(ad_filter, field, min_shown_count, max_shown_number):
    """Сбрасывает счетчик показов для объявлений."""
    if min_shown_count > max_shown_number:
        ad_filter.update(**{field: 0})


def update_vip_advertisements(ad_filter, field_shown, field_count):
    """Обновляет показанные VIP объявления на основе минимальных показов."""
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
    """Ротация VIP объявлений."""
    with transaction.atomic():
        all_ads_vip = Advertisement.objects.filter(moderated=True, is_active=True, vip=True)
        if not all_ads_vip.exists():
            return

        update_vip_advertisements(all_ads_vip, 'shown_vip', 'shown_vip_count')


@shared_task()
def list_shown_vip_category():
    """Ротация VIP объявлений по категориям."""
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
def deactivate_store():
    """ Функция деактивации магазина по истечению времени публикации """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone("Europe/Minsk")
    aware_datetime = current_datetime.astimezone(timezone_now)

    deactivate_stores = Store.objects.filter(date_of_deactivate__lt=aware_datetime, is_active=True)
    deactivate_stores.update(is_active=False)


@shared_task()
def delete_everything_in_folder_beat():
    '''Таска удаляющая все файлы из папки для "files_for_bulk_import_of_ads"
    Таска отрабатывает раз в сутки в 00.00'''
    path = './media/files_for_bulk_import_of_ads'
    shutil.rmtree(path)
    os.mkdir(path)


@shared_task()
def save_many_ads_from_excel_task(uploud_file, id, first_name, phone_number, email):
    '''Таска сохраняющая объявления из экселя'''
    result = save_many_ads_from_excel(uploud_file, id, first_name, phone_number, email)
    return result


@shared_task()
def save_many_ads_from_zip_task(uploud_zip, id, first_name, phone_number, email):
    '''Таска сохраняющая объявления из zip-архива'''
    result = save_many_ads_from_zip(uploud_zip, id, first_name, phone_number, email)
    return result


@shared_task()
def delete_error_file_beat():
    '''Таска удаляющая все экземпляры модели ErrorFile разы в сутки '''
    files = ErrorFile.objects.all()
    files.delete()
