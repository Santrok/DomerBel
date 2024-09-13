import pytz
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from advertisement.models import Advertisement, Store
from advertisement.functions_for_bulk_import import delete_everything_in_folder, save_many_ads_from_excel, \
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
    delete_everything_in_folder()

@shared_task()
def save_many_ads_from_excel_task(uploud_file,id,first_name,phone_number,email):
    '''Таска сохраняющая объявления из экселя'''
    print('start')
    result = save_many_ads_from_excel(uploud_file,id,first_name,phone_number,email)
    print('finish')
    return result

@shared_task()
def save_many_ads_from_zip_task(uploud_zip, id,first_name,phone_number,email):
    '''Таска сохраняющая объявления из zip-архива'''
    result = save_many_ads_from_zip(uploud_zip, id,first_name,phone_number,email)
    return result

@shared_task()
def delete_error_file_beat():
    '''Таска удаляющая все экземпляры модели ErrorFile разы в сутки '''
    files = ErrorFile.objects.all()
    files.delete()
