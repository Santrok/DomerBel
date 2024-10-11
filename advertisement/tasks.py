import os
import shutil
import pytz
import redis

from celery import shared_task
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Q

from config.celery_app import app
from advertisement.models import Advertisement, Store
from advertisement.functions_for_bulk_import import (save_many_ads_from_excel, save_many_ads_from_zip)
from advertisement.models import ErrorFile


def get_current_datetime(timezone_="Europe/Minsk"):
    """Функция возвращает текущее время в часовом поясе"""
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = timezone.now()

    # Преобразуем текущую дату и время в часовой пояс, который вам нужен
    timezone_now = pytz.timezone(timezone_)
    datetime_by_timezone = current_datetime.astimezone(timezone_now)
    return datetime_by_timezone


@shared_task()
def deactivate_advertisement():
    """ Функция деактивации объявлений по истечению времени публикации """
    current_datetime = get_current_datetime()
    deactivate_advertisements = Advertisement.objects.filter(date_of_deactivate__lt=current_datetime, is_active=True)
    deactivate_advertisements.update(is_active=False)

    # deactivate_advertisements = Advertisement.objects.filter(is_active=False)
    # deactivate_advertisements.update(is_active=True)


@shared_task()
def delete_advertisement():
    """ Функция удаления объявлений по истечению времени """
    # Получаем текущую дату и время с информацией о часовом поясе
    current_datetime = get_current_datetime()
    delete_advertisements = Advertisement.objects.filter(date_of_delete__lt=current_datetime, is_active=False)
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
    current_datetime = get_current_datetime()
    deactivate_stores = Store.objects.filter(date_of_deactivate__lt=current_datetime, is_active=True)
    deactivate_stores.update(is_active=False)


@shared_task()
def delete_everything_in_folder_beat():
    """
    Таска удаляющая все файлы из папки для "files_for_bulk_import_of_ads"
    Таска отрабатывает раз в сутки в 00.00"""
    path = './media/files_for_bulk_import_of_ads'
    shutil.rmtree(path)
    os.mkdir(path)


@shared_task()
def save_many_ads_from_excel_task(uploud_file, id, first_name, phone_number, email):
    """Таска сохраняющая объявления из экселя"""
    result = save_many_ads_from_excel(uploud_file, id, first_name, phone_number, email)
    return result


@shared_task()
def save_many_ads_from_zip_task(uploud_zip, id, first_name, phone_number, email):
    """Таска сохраняющая объявления из zip-архива"""
    result = save_many_ads_from_zip(uploud_zip, id, first_name, phone_number, email)
    return result


@shared_task()
def delete_error_file_beat():
    """Таска удаляющая все экземпляры модели ErrorFile разы в сутки"""
    files = ErrorFile.objects.all()
    files.delete()


@shared_task()
def deactivate(args=None):
    print(f"Все сработало как надо {args}")


def create_tasks_from_schedule(name, task, schedule_, args=None, kwargs=None):
    """Функция добавляет периодическую задачи в celery"""
    entry = RedBeatSchedulerEntry(
        name=name,
        task=task,
        schedule=schedule_,
        args=args or [],
        kwargs=kwargs or {},
        app=app
    )
    entry.save()
    print(f"Added periodic task: {name}, {schedule_}")


def delete_task(task_id):
    """Функция удаляет периодическую задачи в celery"""
    try:
        entry = RedBeatSchedulerEntry.from_key(task_id, app=app)
        if entry:
            try:
                entry.delete()  # Пробуем удалить
                print(f"Задача {task_id} успешно удалена.")
            except Exception as e:
                print(f"Ошибка при удалении задачи: {str(e)}")
    except KeyError:
        print(f"Задача {task_id} не найдена.")


def get_list_tasks():
    r = redis.StrictRedis.from_url('redis://localhost:6379/2')

    # Получаем все ключи RedBeat с префиксом 'redbeat:'
    tasks = r.keys('redbeat:*')
    list_tasks = []

    # Отображаем все задачи
    for task in tasks:
        task_name = task.decode('utf-8')
        if task_name.startswith('redbeat:') and '::' not in task_name:
            list_tasks.append(task_name)
            print(task_name)

    return list_tasks


@shared_task()
def deactivation_of_paid_services(ads_id, name_for_delete, **fild_update):
    """Функция отключает выбранную платную услугу и удаляет эту задачу из redbeat:schedule"""
    Advertisement.objects.filter(id=ads_id).update(**fild_update)
    delete_task(name_for_delete)


@shared_task()
def raise_or_deactivation_of_paid_services(ads_id, name_for_delete, **fild_update):
    """Функция поднимает объявления в поиске,
    также отключает платную услугу поднять в поиске и удаляет эту задачу из redbeat:schedule
    """
    current_datetime = get_current_datetime()
    ads = Advertisement.objects.filter(id=ads_id)
    ads.update(search_boost_date=current_datetime)
    if ads.first().date_of_deactivate_special_accommodation.date() == current_datetime.date():
        deactivation_of_paid_services(ads_id, name_for_delete, **fild_update)


# @shared_task()
def update_schedule(data):
    """Функция динамического обновления redbeat:schedule"""
    current_datetime = get_current_datetime()
    list_advertisements_for_deactivate = Advertisement.objects.filter(is_active=True).filter(
        Q(date_of_deactivate_vip__date__lte=current_datetime.date(), vip=True) |
        Q(date_of_deactivate_highlight_ad__date__lte=current_datetime.date(), highlight_ad=True) |
        Q(special_accommodation=True))

    if not list_advertisements_for_deactivate:
        return

    for ads_for_deactivate in list_advertisements_for_deactivate:
        if ads_for_deactivate.vip and ads_for_deactivate.date_of_deactivate_vip.date() <= current_datetime.date():
            name = f'deactivate_advertisement_vip_{ads_for_deactivate.id}'
            schedule_ = crontab(hour=ads_for_deactivate.date_of_deactivate_vip.hour,
                                minute=ads_for_deactivate.date_of_deactivate_vip.minute)

            if ads_for_deactivate.date_of_deactivate_vip < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour,
                                    minute=current_datetime.minute + 1)

            create_tasks_from_schedule(name,
                                       "advertisement.tasks.deactivation_of_paid_services",
                                       schedule_,
                                       [ads_for_deactivate.id, f'redbeat:{name}'],
                                       {'vip': False})

        if ads_for_deactivate.highlight_ad and ads_for_deactivate.date_of_deactivate_highlight_ad <= current_datetime:
            name = f'deactivate_advertisement_highlight{ads_for_deactivate.id}'
            schedule_ = crontab(hour=ads_for_deactivate.date_of_deactivate_highlight_ad.hour,
                                minute=ads_for_deactivate.date_of_deactivate_highlight_ad.minute)

            if ads_for_deactivate.date_of_deactivate_highlight_ad < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour,
                                    minute=current_datetime.minute + 1)

            create_tasks_from_schedule(name,
                                       "advertisement.tasks.deactivation_of_paid_services",
                                       schedule_,
                                       [ads_for_deactivate.id, f'redbeat:{name}'],
                                       {'highlight_ad': False})

        if ads_for_deactivate.date_of_deactivate_special_accommodation:
            name = f'raise_or_deactivate_advertisement_special_accommodation_{ads_for_deactivate.id}'
            schedule_ = crontab(hour=ads_for_deactivate.date_of_deactivate_special_accommodation.hour + 3,
                                minute=ads_for_deactivate.date_of_deactivate_special_accommodation.minute)
            task = "advertisement.tasks.raise_or_deactivation_of_paid_services"

            if ads_for_deactivate.date_of_deactivate_special_accommodation < current_datetime:
                schedule_ = crontab(hour=current_datetime.hour,
                                    minute=current_datetime.minute + 1)
                task = "advertisement.tasks.deactivation_of_paid_services"
            create_tasks_from_schedule(name,
                                       task,
                                       schedule_,
                                       [ads_for_deactivate.id, f'redbeat:{name}'],
                                       {'special_accommodation': False})
