import random

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, F
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from config.settings import env_keys
from related_data.models import Category, Region
from related_data.utils import (get_region_variables, create_variables_for_filter_and_bread_crumbs,
                                forming_fields_for_annotation_and_search)
from utils.template_paginator import variables_for_paginator
from .forms import ComplaintForm, UploadFileForm
from .models import Advertisement, UploadFile
from .utils import (setting_values_for_sorting_from_cookie_or_request_get, get_additional_data_for_advertisement,
                    get_similar_advertisement, make_clear_query, setting_search_options,
                    get_result_for_filter_advertisement_query)


def get_advertisement_page(request):
    """
    Сборка страницы 'Объявления'.
    Модели: Advertisement, Category
    """
    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    (region_filter,
     region_param,
     region_bread_crumbs) = get_region_variables(request.GET.get('region'))

    advertisements = Advertisement.objects.filter(is_active=True,
                                                  moderated=True,
                                                  **region_filter).select_related(
        'category',
        'region'
    ).order_by(order_by).defer(
        'search_title_vector',
        'search_vector',
        'video_link',
        'description',
        'additional_information_view',
        'additional_information',
        'store',
        'contact_name',
        'counter_views',
        'phone_num')
    vip_advertisements = advertisements.filter(vip=True, shown_vip=True, is_active=True, moderated=True)
    categories = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                    Advertisement,
                                                    'category',
                                                    'advertisement_counts',
                                                    cumulative=True,
                                                    extra_filters={"is_active": True,
                                                                   "moderated": True,
                                                                   **region_filter})

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        "ads_found": advertisements.count(),
        "category": categories,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        "vip_advertisement": vip_advertisements,
        'date': state_sort_by_date,
        'adaptive_navigation': "Доска объявлений. Беларусь",
    }

    response = render(request, "advertisement.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


def get_advertisement_by_category(request, category_slug):
    """
    Сборка страницы с объявлениями по конкретной категории.
    Модели: Advertisement, Category
    """
    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    (region_filter,
     region_param,
     region_bread_crumbs) = get_region_variables(request.GET.get('region'))

    categories_all = Category.objects.all()
    category = get_object_or_404(categories_all, slug=category_slug)
    category_bread_crumbs = category.get_ancestors(ascending=False, include_self=True)
    annotated_categories = Category.objects.add_related_count(category.get_descendants(),
                                                              Advertisement,
                                                              'category',
                                                              'advertisement_counts',
                                                              cumulative=True,
                                                              extra_filters={"is_active": True,
                                                                             "moderated": True,
                                                                             **region_filter})
    categories = annotated_categories.filter(parent_id=category.id)
    advertisements = Advertisement.objects.filter(Q(category__in=annotated_categories) |
                                                  Q(category__slug=category.slug),
                                                  **region_filter,
                                                  is_active=True,
                                                  moderated=True).select_related(
        'category',
        'region').order_by(order_by).defer(
        'search_title_vector',
        'search_vector',
        'video_link',
        'description',
        'additional_information_view',
        'additional_information',
        'store',
        'contact_name',
        'counter_views',
        'phone_num')

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if categories:
        vip_advertisements_in_category = Advertisement.objects.filter(category__in=categories,
                                                                      vip=True,
                                                                      shown_vip_category=True,
                                                                      is_active=True,
                                                                      moderated=True).distinct('category')
        # Получаем список уникальных категорий из найденных VIP-объявлений
        vip_categories = vip_advertisements_in_category.values_list('category', flat=True)
        # Если есть VIP-объявления в категориях, выбираем случайную категорию
        if vip_categories.exists():
            random_category = random.choice(vip_categories)  # Выбираем случайную категорию
            vip_advertisement = advertisements.filter(category=random_category,
                                                      vip=True,
                                                      shown_vip_category=True,
                                                      is_active=True,
                                                      moderated=True)
        else:
            vip_advertisement = advertisements.filter(vip=True,
                                                      shown_vip_category=True,
                                                      is_active=True,
                                                      moderated=True)

    else:
        vip_advertisement = advertisements.filter(vip=True,
                                                  shown_vip_category=True,
                                                  is_active=True,
                                                  moderated=True)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)
    context = {
        "ads_found": advertisements.count(),
        "category": categories,
        "region_param": region_param,
        "category_bread_crumbs": category_bread_crumbs,
        "region_bread_crumbs": region_bread_crumbs,
        "page_obj": page_obj,
        "vip_advertisement": vip_advertisement,
        'date': state_sort_by_date,
        'adaptive_navigation': f"{category.main_title if category.main_title else category.title}. Беларусь",
    }

    response = render(request, "advertisement.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


def get_page_place_an_advertisement(request):
    """
    Сборка страницы для создания нового объявления.
    Сохранение объявления выполняется в функции save_advertisement.
    Модели: Advertisement, Category, Region
    """
    category_list = Category.objects.filter(level__lte=1)
    oblast = Region.objects.filter(level=0).order_by('id')
    categories = Category.objects.filter(level=0)

    context = {
        "category_list": category_list,
        'adaptive_navigation': "Добавление объявления",
        'oblast': oblast,
        'categories': categories,
    }

    return render(request, 'advertisement_place_an_ad.html', context)


@login_required
def get_page_editing_an_advertisement(request, id):
    """
    Сборка страницы для редактирования объявления.
    Изменение объявления выполняется в функции update_advertisement.
    Модели: Advertisement, Category, Region, ElementTwo
    """
    advertisement = get_object_or_404(Advertisement, id=id, author=request.user)

    region = Region.objects.all()
    oblast = Region.objects.filter(level=0)
    selected_oblast = region.get(id=advertisement.region.parent_id)
    cities = advertisement.region.get_siblings(include_self=True)
    family_categories = advertisement.category.get_family()

    list_categories = [category.get_siblings(include_self=True) for category in family_categories]
    categories = {key: value for key, value in zip(family_categories, list_categories)}

    (additional_information,
     additional_values,
     additional_values_two) = get_additional_data_for_advertisement(advertisement)

    context = {
        'advertisement': advertisement,
        'oblast': oblast,
        'selected_oblast': selected_oblast,
        'cities': cities,
        'categories': categories,
        'additional_information': additional_information,
        'additional_values': additional_values,
        'additional_values_two': additional_values_two,
    }
    return render(request, 'advertisement_editing_an_ad.html', context)


def get_advertisement_details_page(request, slug):
    """
    Сборка страницы с детальным описанием объявления.
    Модели: Advertisement, ReasonOfComplaint.
    Формы: ComplaintForm.
    """
    main_advertisement = get_object_or_404(Advertisement.objects.prefetch_related("photoadvertisement_set"), slug=slug)

    if main_advertisement.moderated or main_advertisement.author == request.user or request.user.is_staff:
        Advertisement.objects.filter(id=main_advertisement.id).update(counter_views=F("counter_views") + 1)
        category_crumbs = main_advertisement.category.get_ancestors(ascending=False, include_self=True)
        similar_advertisement = get_similar_advertisement(main_advertisement)

        complaint_form = ComplaintForm()
        context = {
            "advertisement": main_advertisement,
            "category_crumbs": category_crumbs,
            "similar_advertisement": similar_advertisement,
            "form": complaint_form,
            "adaptive_navigation": f"{main_advertisement.title}.",
        }
        return render(request=request,
                      template_name='advertisement_details.html',
                      context=context)
    else:
        raise Http404


def get_page_search_result_by_advertisements(request):
    """
    Сборка страницы с результатами поиска по объявлениям.
    Модели: Advertisement, Category, Region
    """
    categories = []
    copy_of_request_get = dict.copy(request.GET)

    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    category, category_bread_crumbs = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('category',
                                                                                                           None),
                                                                                   Category)
    region, region_bread_crumbs = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('region',
                                                                                                       None),
                                                                               Region)

    query, copy_of_request_get = make_clear_query(request.META.get('QUERY_STRING'), copy_of_request_get, request.GET)
    field_for_search, search_lookup, field_annotate = forming_fields_for_annotation_and_search(copy_of_request_get)

    search_parameters = setting_search_options(category=category,
                                               region=region,
                                               only_photo=request.GET.get('only_photo'),
                                               only_video=request.GET.get('only_video'),
                                               only_title=request.GET.get('only_title'),
                                               text_search=request.GET.get('text_search'),
                                               field_for_search=field_for_search,
                                               search_lookup=search_lookup)

    try:
        categories_annotate = Category.objects.add_related_count(category.get_descendants() if
                                                                 category else
                                                                 Category.objects.root_nodes(),
                                                                 Advertisement,
                                                                 'category',
                                                                 'advertisement_counts',
                                                                 cumulative=True,
                                                                 extra_filters={"is_active": True,
                                                                                "moderated": True,
                                                                                **search_parameters
                                                                                })
        if request.GET.get('category'):
            categories = categories_annotate.filter(parent_id=request.GET.get('category'))
    except Exception as e:
        # Логирование
        print(f"Error fetching categories: {e}")
    advertisements = get_result_for_filter_advertisement_query(search_parameters,
                                                               field_annotate,
                                                               search_lookup,
                                                               order_by=order_by)

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        "ads_found": advertisements.count(),
        "page_obj": page_obj,
        "region_bread_crumbs": region_bread_crumbs,
        "category_bread_crumbs": category_bread_crumbs,
        "category": categories if request.GET.get('category') else categories_annotate,
        "query": query,
        'date': state_sort_by_date,
        'adaptive_navigation': 'Результаты поиска'
    }
    response = render(request, "advertisement_search_result.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


@login_required
@permission_required("advertisement.view_uploadfile", raise_exception=True)
def get_page_for_bulk_import_of_advertisement(request):
    """
    Сборка страницы массового импорта объявлений.
    Модели: UploadFile
    """
    files = UploadFile.objects.select_related('errorfile').filter(user=request.user).order_by('-time_upload_file')
    url = env_keys.get('URL')
    context = {
        'files': files,
        'form': UploadFileForm(),
        'url': url,
        'adaptive_navigation': 'Массовый импорт объявлений'
    }
    return render(request=request,
                  template_name='advertisement_bulk_import_ads.html',
                  context=context)


def get_page_for_instructions_for_bulk_import_of_ads(request):
    """
    Сборка страницы с инструкцией по массовому импорту объявлений.
    Модели: Region, Category
    """
    oblast = Region.objects.filter(level=0)
    categories = Category.objects.filter(level=0)
    url = env_keys.get('URL')
    context = {
        'oblast': oblast,
        'categories': categories,
        'url': url,
        'adaptive_navigation': 'Массовый импорт объявлений'
    }
    return render(request=request,
                  template_name='advertisement_instructions_for_bulk_import_of_ads.html',
                  context=context)
