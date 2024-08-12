from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Region


def sorted_by_number(number):
    if (number == '30'
            or number == '60'
            or number == '90'):
        sort_for_paginator = int(number)
        return sort_for_paginator
    else:
        return 30


def variables_for_paginator(queryset, page=1, elements=30):
    paginator = Paginator(queryset, elements)
    page_number = page
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


def get_region_variables(region_request):
    if region_request:
        region_filter = dict(
            region__in=Region.objects.filter(id=region_request).get_descendants(include_self=True))
        region_param = get_object_or_404(Region, id=region_request)
        region_bread_crumbs = region_param.get_ancestors(ascending=False, include_self=True)
        return region_filter, region_param, region_bread_crumbs
    else:
        region_filter = dict(region__in=Region.objects.all())
        region_bread_crumbs = ''
        region_param = ''
        return region_filter, region_param, region_bread_crumbs


def where_to_look(parameter, model):
    result = []
    bread_crumbs = []
    if parameter:
        if parameter == ['']:
            pass
        else:
            while '' in parameter:
                parameter.remove('')
            result = get_object_or_404(model, id=parameter[-1]).get_descendants(include_self=True)
            bread_crumbs = get_object_or_404(model, id=parameter[-1]).get_ancestors(ascending=False, include_self=True)
    return result, bread_crumbs


def search_additional_information(fild, cop):
    search = {}
    search_kt = {}
    for i in fild:
        if "от" not in i.search and cop.get(f'{i.id}') != ['undefined']:
            print(cop.get(f'{i.id}'))
            if len(cop.get(f'{i.id}')) > 1 and i.title == 'Этаж':
                if cop.get(f'{i.id}') == ['undefined', 'undefined']:
                    pass
                elif cop.get(f'{i.id}')[0] == 'undefined':
                    search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace('undefined,', ',')
                else:
                    search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace(', undefined', ',')
            elif len(cop.get(f'{i.id}')) > 1:
                search_kt[i.title] = ', '.join(cop.get(f'{i.id}')).replace(', undefined', '')
            else:
                search[i.title] = ', '.join(cop.get(f'{i.id}'))
        elif cop.get(f'{i.id}') != ['undefined']:
            search_kt[i.title] = cop.get(f'{i.id}')
    return search, search_kt


def annotating_field(kt):
    search_q = {}
    search_annotate = {}
    for i, item in enumerate(kt):
        search_annotate[f"find{i}"] = f"additional_information__{item}"
        if type(kt.get(item)) is not str:
            for index, x in enumerate(kt.get(item)):
                if x != 'undefined':
                    if index == 0:
                        search_q[f"find{i}__gte"] = x
                    elif index == 1:
                        search_q[f"find{i}__lte"] = x
        else:
            search_q[f"find{i}__icontains"] = kt.get(item)

    return search_q, search_annotate
