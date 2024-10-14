from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Region, Field


def get_region_variables(region_request):
    """
    Функция формирования списка данных для фильтра,
    создания хлебных крошек и получение выбранного экземпляра модели Region.
    Можно использовать только для Mptt моделей.
    """
    if not region_request:
        return dict(region__in=Region.objects.all()), None, None
    region_param = get_object_or_404(Region, id=region_request)
    region_filter, region_bread_crumbs = create_variables_for_filter_and_bread_crumbs([region_request],
                                                                                      Region)
    return dict(region__in=region_filter), region_param, region_bread_crumbs


def create_variables_for_filter_and_bread_crumbs(parameter, model):
    """
    Функция формирования списка данных для фильтра,
    а так же создания хлебных крошек для страниц с результатами поиска.
    Можно использовать только для Mptt моделей.
    """
    result = []
    bread_crumbs = []
    if parameter and parameter != ['']:
        if type(parameter) is not str:
            while '' in parameter:
                parameter.remove('')
        result = _create_variables_for_filter(parameter, model)
        bread_crumbs = _create_variables_for_bread_crumbs(parameter, model)
    return result, bread_crumbs


def _create_variables_for_bread_crumbs(parameter, model):
    """
    Функция формирования хлебных крошек.
    Можно использовать только для Mptt моделей.
    """
    return get_object_or_404(model, id=parameter[-1]).get_ancestors(ascending=False, include_self=True)


def _create_variables_for_filter(parameter, model):
    """
    Функция формирования списка данных для фильтра.
    Можно использовать только для Mptt моделей.
    """
    return get_object_or_404(model, id=parameter[-1]).get_descendants(include_self=True)


def _make_field_for_search_by_additional_information(copy_of_request_get):
    """
    Формирует словарь для дальнейшего поиска по полю "дополнительная информация" объявления,
    формирует словарь для дальнейшей аннотации переменных поля "дополнительная информация" объявления
    """
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
    """
    Обработка значений для поля 'Этаж'.
    """
    clean_values = [x for x in field_value if x != 'undefined']
    return ', '.join(clean_values).strip(', ')


def _make_annotated_fields(kt):
    """
    Формирует название полей для дальнейшей аннотации и формирует lookup со значением для поиска по полю
    additional_information модели Advertisement.
    """
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
    """
    Формирует поля для аннотации и поиска
    """
    field_for_search, field_for_annotate = _make_field_for_search_by_additional_information(copy_of_request_get)
    search_lookup, field_annotate = _make_annotated_fields(field_for_annotate)
    return field_for_search, search_lookup, field_annotate
