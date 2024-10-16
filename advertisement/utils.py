import random
from datetime import datetime, timedelta

from django.db.models import Func, FloatField
from django.db.models.fields.json import KT
from django.utils.timezone import get_current_timezone

from advertisement.models import Advertisement
from related_data.models import ElementTwo


def setting_values_for_sorting_from_cookie_or_request_get(cookie, parameters_from_request_get):
    """
    Функция принимающая COOKIE и параметры GET запроса для
    установки значений переменных для дальнейшей сортировки
    """
    if parameters_from_request_get.get('sort'):
        sort_for_paginator = _sorted_by_number(parameters_from_request_get.get('sort'))
    else:
        sort_for_paginator = _sorted_by_number(cookie.get('sort'))
    if parameters_from_request_get.get('date') or parameters_from_request_get.get('price'):
        state_sort_by_date, order_by = _sorted_by_date_or_price(parameters_from_request_get)
    else:
        state_sort_by_date = cookie.get('date', 0)
        order_by = _sorted_by(cookie.get('sorted_by'))
    return order_by, sort_for_paginator, state_sort_by_date


def _sorted_by_number(number):
    """
    Возвращает число для сортировки количества объявлений если оно разрешено
    """
    number_list = ["30", "60", "90"]
    if number in number_list:
        return int(number)
    return 30


def _sorted_by_date_or_price(sort):
    """
    Возвращает значения для установки значения сортировки
    """
    if sort.get('date'):
        if sort['date'] == '0':
            return 1, 'search_boost_date'
        else:
            return 0, "-search_boost_date"
    elif sort.get('price'):
        if sort['price'] == '0':
            return 1, 'price'
        else:
            return 0, '-price'
    return 0, "-search_boost_date"


def _sorted_by(key):
    """
    Возвращает вариант сортировки, если он разрешен
    """
    key_list = ["-search_boost_date", "search_boost_date", 'price', '-price']
    if key in key_list:
        return key
    else:
        return "-search_boost_date"


def get_similar_advertisement(advertisement):
    """
    Возвращает схожие экземпляры модели Advertisement созданные за последние 50 дней.
    Модели: Advertisement
    """
    date = datetime.now(tz=get_current_timezone()) - timedelta(days=50)
    similar_advertisement = list(Advertisement.objects.filter(moderated=True,
                                                              is_active=True,
                                                              category_id=advertisement.category,
                                                              date_of_last_activation__date__gte=date
                                                              ).exclude(id=advertisement.id).values_list('id',
                                                                                                         flat=True))

    similar_advertisement = random.sample(similar_advertisement,
                                          4 if len(similar_advertisement) >= 4 else len(similar_advertisement))
    similar_advertisement = Advertisement.objects.filter(id__in=similar_advertisement)
    return similar_advertisement


def get_additional_data_for_advertisement(advertisement):
    """
    Возвращает дополнительные данные объявления.
    Модели: Advertisement, Category, Field, ElementTwo
    """
    additional_information = advertisement.category.field_set.all().prefetch_related("spisok")

    additional_values = {key: value for key, value in zip(advertisement.additional_information.keys(),
                                                          map(lambda i: i.split(", "),
                                                              advertisement.additional_information.values()))}

    additional_values_two = {}
    for i in additional_values.items():
        if len(i[1]) > 1:
            additional_values_two[i[0]] = [i[1][0], ElementTwo.objects.filter(element__title=i[1][0])]
    for i in additional_information:
        if i.min_val_interval_date:
            additional_values_two[i.title] = [str(date) for date in
                                              range(i.min_val_interval_date, i.max_val_interval_date + 1)]
    return additional_information, additional_values, additional_values_two


def setting_search_options(category=None, region=None, only_photo=None, only_video=None,
                           only_title=None, text_search=None, field_for_search=None, search_lookup=None, id=None):
    """
    Возвращает словарь из параметров для дальнейшего поиска
    """
    search_parameters = {}
    if category:
        search_parameters['category__in'] = category
    if region:
        search_parameters['region__in'] = region
    if only_photo:
        search_parameters['preview_image__gt'] = ''
    if only_video:
        search_parameters['video_link__isnull'] = False
    if only_title and text_search:
        search_parameters['search_title_vector'] = text_search
    elif text_search:
        search_parameters['search_vector'] = text_search
    if field_for_search:
        search_parameters['additional_information__contains'] = field_for_search
    if search_lookup:
        search_parameters.update(search_lookup)
    if id:
        search_parameters['id'] = id
    return search_parameters


def make_clear_query(query, copy_of_request_get, request_get):
    """
    Возвращает копии query и request.GET без параметров сортировки
    """
    key_delete = ['page', 'sort', 'date', 'price', 'text_search',
                  'only_photo', 'only_video', 'only_title', 'id', 'active']
    for key in key_delete:
        query = query.replace(f'{key}={request_get.get(key)}&', '')
        copy_of_request_get.pop(key, None)
    return query, copy_of_request_get


def get_result_for_filter_advertisement_query(search_parameters, field_annotate, search_lookup, is_active=True,
                                              moderated=True, order_by="-search_boost_date", **kwargs):
    """
    Возвращает результат запроса поиска по объявлениям
    """
    advertisements = Advertisement.objects.annotate(**{key: Func(KT(value), function='CAST',
                                                                 template='CAST(%(expressions)s AS numeric)',
                                                                 output_field=FloatField()) if search_lookup.get(
        f'{key}__lte') or search_lookup.get(f'{key}__gte') else KT(value) for key, value in field_annotate.items()}
                                                    ).filter(is_active=is_active,
                                                             moderated=moderated,
                                                             **search_parameters,
                                                             **kwargs
                                                             ).select_related('category',
                                                                              'region'
                                                                              ).order_by(order_by)

    return advertisements
