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


@shared_task()
def list_shown_vip():
    """ Меняет объявления для показа """
    with (transaction.atomic()):

        # Получаем все вип объявления
        all_ads_vip = Advertisement.objects.filter(vip=True)

        # Проверяем если ли вообще объявления
        if not all_ads_vip.exists():
            print('no vip')
            return

        # Получаем активные для показа vip объявления
        total_vip_count = all_ads_vip.count()
        all_ads_shown_vip_count = all_ads_vip.filter(shown_vip=True).count()

        # Если vip объявлений меньше или равно 3 и есть all_ads_shown_vip False
        if 3 >= total_vip_count != all_ads_shown_vip_count:
            print(f'Меньше 3: {all_ads_shown_vip_count} - {all_ads_vip.count()}')
            all_ads_vip.update(shown_vip=True)
            return

        # Если больше 3, то запускай процедуру изменения показываемых объявлений
        if total_vip_count > 3:
            print(f'Меняю: {all_ads_shown_vip_count}')

            # Деактивируем все вип объявления
            all_ads_vip.update(shown_vip=False)

            # Отбираем все VIP объявления
            vip_ads = all_ads_vip.order_by('shown_vip_count')

            # Проверяем, сколько раз объявление было показано (все ли объявления показаны одинаково)
            min_shown_count = vip_ads.first().shown_vip_count

            # Возможно это не надо от слова совсем !!!!!!!!!!!!!!!!!!
            # Сбрасываем счетчик если объявления показаны больше 100 раз
            if min_shown_count > 100:
                all_ads_vip.update(shown_vip_count=0)
                vip_ads = all_ads_vip.order_by('shown_vip_count')

            # Отбираем три объявления с минимальным количеством показов
            ads_to_show = vip_ads.filter(shown_vip_count=min_shown_count)[:3]

            # Если нашлось меньше трёх объявлений, добираем оставшиеся из списка
            if ads_to_show.count() < 3:
                remaining_ads = vip_ads.exclude(id__in=ads_to_show
                                                ).order_by('shown_vip_count')[:3 - ads_to_show.count()]
                ads_to_show = ads_to_show.union(remaining_ads)

            # Обновляем счетчик показов для выбранных объявлений
            Advertisement.objects.filter(id__in=[ad.id for ad in ads_to_show]
                                         ).update(shown_vip=True,
                                                  shown_vip_count=F('shown_vip_count') + 1)
        else:
            print(f'Не меняю: {all_ads_vip.filter(shown_vip=True).count()}')


@shared_task()
def reset_shown_vip_count():
    """ Сбрасывает счетчик shown_vip_count на 0 в отпределенное время """
    with (transaction.atomic()):
        # Сбрасываем счетчики вип объявлений на ноль
        Advertisement.objects.filter(vip=True).update(shown_vip_count=0)


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
    print('start')
    result = save_many_ads_from_excel(uploud_file, id, first_name, phone_number, email)
    print('finish')
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
