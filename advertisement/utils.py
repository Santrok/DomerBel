from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Region, Field


def sorted_by_number(number):
    """Функция для сортировки"""
    if number == '30' or number == '60' or number == '90':
        return int(number)
    return 30


def variables_for_paginator(queryset, page_number=1, elements=30):
    # paginator
    """Функция для формирования пагинатора"""
    paginator = Paginator(queryset, elements)
    page_obj = paginator.get_page(page_number)
    return page_obj


def sorted_by_date_or_price(sort):
    if sort.get('date'):
        if sort['date'] == '0':
            return 1, 'date_of_create'
        else:
            return 0, '-date_of_create'
    elif sort.get('price'):
        if sort['price'] == '0':
            return 1, 'price'
        else:
            return 0, '-price'


def sorted_by(key):
    if key == '-date_of_create' or key == 'date_of_create' or key == 'price' or key == '-price':
        return key
    else:
        return '-date_of_create'


def setting_values_for_sorting_from_cookie_or_request_get(cookie, parameters_from_request_get):
    # вынести в utils приложения advertisement
    """Функция принимающая COOKIE и параметры GET запроса для
        установки значений переменных для дальнейшей сортировки"""
    if parameters_from_request_get.get('sort'):
        sort_for_paginator = sorted_by_number(parameters_from_request_get.get('sort'))
    else:
        sort_for_paginator = sorted_by_number(cookie.get('sort'))
    if parameters_from_request_get.get('date') or parameters_from_request_get.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(parameters_from_request_get)
    else:
        state_sort_by_date = cookie.get('date', 0)
        order_by = sorted_by(cookie.get('sorted_by'))
    return order_by, sort_for_paginator, state_sort_by_date


def get_region_variables(region_request):
    # в utils приложения category region
    """Функция формирования списка данных для фильтра,
            создания хлебных крошек и получение выбранного экземпляра модели Region.
             Можно использовать только для Mptt моделей."""
    if not region_request:
        return dict(region__in=Region.objects.all()), None, None
    region_param = get_object_or_404(Region, id=region_request)
    region_filter, region_bread_crumbs = where_to_look([region_request], Region)
    return dict(region__in=region_filter), region_param, region_bread_crumbs


def where_to_look(parameter, model):
    # в utils приложения category region
    # create_variables_for_filter_and_bread_crumbs
    """Функция формирования списка данных для фильтра,
        а так же создания хлебных крошек для страниц с результатами поиска.
         Можно использовать только для Mptt моделей."""
    result = []
    bread_crumbs = []
    if parameter and parameter != ['']:
        while '' in parameter:
            parameter.remove('')
        result = create_variables_for_filter(parameter, model)
        bread_crumbs = create_variables_for_bread_crumbs(parameter, model)
    return result, bread_crumbs


def create_variables_for_bread_crumbs(parameter, model):
    # в utils приложения category region
    """Функция формирования хлебных крошек"""
    return get_object_or_404(model, id=parameter[-1]).get_ancestors(ascending=False, include_self=True)


def create_variables_for_filter(parameter, model):
    # в utils приложения category region
    """Функция формирования списка данных для фильтра"""
    return get_object_or_404(model, id=parameter[-1]).get_descendants(include_self=True)


# def search_additional_information(cop):
#     search = {}
#     search_kt = {}
#     try:
#         for i in Field.objects.filter(id__in=cop.keys()):
#             if "от" not in i.search and cop.get(f'{i.id}') != ['undefined']:
#                 if len(cop.get(f'{i.id}')) > 1 and i.title == 'Этаж':
#                     if cop.get(f'{i.id}') == ['undefined', 'undefined']:
#                         pass
#                     elif cop.get(f'{i.id}')[0] == 'undefined':
#                         search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace('undefined,', ',')
#                     else:
#                         search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace(', undefined', ',')
#                 elif len(cop.get(f'{i.id}')) > 1:
#                     search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace(', undefined', '')
#                 else:
#                     search[i.title] = ', '.join(cop.get(f'{i.id}'))
#             elif cop.get(f'{i.id}') != ['undefined']:
#                 search_kt[i.title] = cop.get(f'{i.id}')
#         return search, search_kt
#     except:
#         raise Http404()


def search_additional_information(copy_of_request_get):
    # make_field_for_search_by_additional_information
    """Формирует словарь для дальнейшего поиска
         по полю "дополнительная информация" объявления,
          формирует словарь для дальнейшей аннотации переменных
           поля "дополнительная информация" объявления"""
    field_for_search = {}
    field_for_annotate = {}
    try:
        fields = Field.objects.filter(id__in=copy_of_request_get.keys())
    except:
        Http404
    else:
        for field in fields:
            field_value = copy_of_request_get.get(str(field.id), [])

            if "от" in field.search or field_value == ['undefined']:
                field_for_annotate[field.title] = field_value
                continue

            if len(field_value) > 1 and field.title == 'Этаж':
                field_for_annotate[field.title] = _handle_floor_field(field_value)
            elif len(field_value) > 1:
                field_for_annotate[field.title] = ', '.join(filter(lambda x: x != 'undefined', field_value))
            else:
                field_for_search[field.title] = ', '.join(field_value)

        return field_for_search, field_for_annotate


def _handle_floor_field(field_value):
    """Обработка значений для поля 'Этаж'."""
    clean_values = [x for x in field_value if x != 'undefined']
    return ', '.join(clean_values).strip(', ')


def annotating_field(kt):
    # make_annotated_fields
    """Формирует название полей для дальнейшей аннотации
        и формирует lookup со значением для поиска по полю
         additional_information модели Advertisement."""
    search_lookup = {}
    field_annotate = {}

    for index, item in enumerate(kt):
        field_annotate[f"find{index}"] = f"additional_information__{item}"
        values = kt.get(item)

        if isinstance(values, list):
            for sub_index, value in enumerate(values):
                if value != 'undefined':
                    if sub_index == 0:
                        search_lookup[f"find{index}__gte"] = value
                    elif sub_index == 1:
                        search_lookup[f"find{index}__lte"] = value
        elif isinstance(values, str):
            if not values.startswith(','):
                search_lookup[f"find{index}__startswith"] = values
            else:
                search_lookup[f"find{index}__endswith"] = values

    return search_lookup, field_annotate


def forming_fields_for_annotation_and_search(copy_of_request_get):
    """Формирует поля для аннотации и поиска"""
    field_for_search, field_for_annotate = search_additional_information(copy_of_request_get)
    search_lookup, field_annotate = annotating_field(field_for_annotate)
    return field_for_search, search_lookup, field_annotate
