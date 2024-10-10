from django.core.paginator import Paginator


def variables_for_paginator(queryset, page_number=1, elements=30):
    """Функция для формирования пагинатора"""
    paginator = Paginator(queryset, elements)
    page_obj = paginator.get_page(page_number)
    return page_obj
