from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from advertisement.models import Advertisement
from advertisement.utils import setting_search_options, setting_values_for_sorting_from_cookie_or_request_get, \
    make_clear_query, get_result_for_filter_advertisement_query
from related_data.models import Category, Region
from related_data.utils import create_variables_for_filter_and_bread_crumbs, get_region_variables, \
    forming_fields_for_annotation_and_search
from utils.template_paginator import variables_for_paginator
from .forms import StoreForm
from .models import Store


# Create your views here.


def get_stores_page(request):
    """
    Сборка страницы "Магазины".
    Модели: Store, Category
    """
    stores = Store.objects.filter(is_active=True).select_related('category', 'region')
    categories = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                    Store,
                                                    'category',
                                                    'store_counts',
                                                    cumulative=True,
                                                    extra_filters={"is_active": True})

    page_obj = variables_for_paginator(stores,
                                       request.GET.get('page'),
                                       10)
    context = {
        "stores_found": stores.count(),
        "category": categories,
        "page_obj": page_obj,
        'adaptive_navigation': 'Магазины. Беларусь'
    }

    return render(request, 'stores.html', context)


def get_store_search_page(request):
    """
    Сборка страницы с результатами поиска по магазинам.
    Модели: Store, Category, Region
    """

    category, category_bread_crumbs = create_variables_for_filter_and_bread_crumbs(request.GET.getlist("category"),
                                                                                   Category)
    region, region_bread_crumbs = create_variables_for_filter_and_bread_crumbs(request.GET.getlist("region"),
                                                                               Region)

    query = request.META.get('QUERY_STRING').replace(f'page={request.GET.get("page")}&', '')

    search_parameters = setting_search_options(category=category,
                                               region=region,
                                               text_search=request.GET.get('text_search'))

    stores = Store.objects.filter(is_active=True, **search_parameters).select_related('category', 'region')
    categories = Category.objects.add_related_count(category.get_descendants() if category
                                                    else Category.objects.root_nodes(),
                                                    Store,
                                                    'category',
                                                    'store_counts',
                                                    cumulative=True,
                                                    extra_filters={"is_active": True,
                                                                   **search_parameters})

    page_obj = variables_for_paginator(stores,
                                       request.GET.get('page'),
                                       10)

    context = {
        "stores_found": stores.count(),
        "category": categories,
        "query": query,
        "page_obj": page_obj,
        'adaptive_navigation': 'Магазины. Результат поиска'
    }

    return render(request, 'stores_search_result.html', context)


def get_stores_by_category(request, category_slug):
    """
    Сборка страницы с магазинами в выбранной категории.
    Модели: Store, Category, Region
    """
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))
    category = get_object_or_404(Category, slug=category_slug)
    categories_annotate = Category.objects.add_related_count(category.get_descendants(),
                                                             Store,
                                                             'category',
                                                             'store_counts',
                                                             cumulative=True,
                                                             extra_filters={"is_active": True,
                                                                            **region_filter})
    stores = Store.objects.filter(Q(category__in=categories_annotate) |
                                  Q(category__slug=category.slug),
                                  **region_filter,
                                  is_active=True).select_related('category',
                                                                 'region')

    page_obj = variables_for_paginator(stores,
                                       request.GET.get('page'),
                                       10)
    context = {
        "stores_found": stores.count(),
        "category": categories_annotate,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        "adaptive_navigation": f"Магазины. {category.main_title if category.main_title else category.title}. Беларусь"
    }
    return render(request, 'stores.html', context)


def get_store_by_title(request, store_slug):
    """
    Сборка страницы с детальной информацией выбранного магазина и его объявлениями.
    Модели: Store, Advertisement, Category, Region
    """
    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    store = get_object_or_404(Store, slug=store_slug)
    advertisements = Advertisement.objects.filter(store=store,
                                                  is_active=True,
                                                  moderated=True,
                                                  **region_filter
                                                  ).select_related('category',
                                                                   'region').order_by(order_by)
    categories_annotate = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                             Advertisement,
                                                             'category',
                                                             'advertisement_counts',
                                                             cumulative=True,
                                                             extra_filters={**region_filter,
                                                                            "store": store,
                                                                            "is_active": True,
                                                                            "moderated": True
                                                                            })

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        'store': store,
        "ads_found": advertisements.count(),
        "category": categories_annotate,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        'date': state_sort_by_date,
        'adaptive_navigation': f'{store.title}. Беларусь'

    }
    response = render(request, 'store_details.html', context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)
    response.set_cookie('user_auth', request.user.id)

    return response


def get_store_by_title_and_category(request, store_slug, category_slug):
    """
    Сборка страницы с детальной информацией выбранного магазина
    и его объявлениями в выбранной категории.
    Модели: Store, Advertisement, Category, Region
    """
    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    store = get_object_or_404(Store, slug=store_slug)
    category = get_object_or_404(Category, slug=category_slug)
    category_bread_crumbs = category.get_ancestors(ascending=False, include_self=True)
    categories_annotate = Category.objects.add_related_count(category.get_descendants(),
                                                             Advertisement,
                                                             'category',
                                                             'advertisement_counts',
                                                             cumulative=True,
                                                             extra_filters={
                                                                 "region__in": region_filter['region__in'],
                                                                 "store": store,
                                                                 "is_active": True,
                                                                 "moderated": True
                                                             }).filter(parent_id=category.id)
    advertisements = Advertisement.objects.filter(Q(category__in=categories_annotate) |
                                                  Q(category__slug=category.slug),
                                                  store=store,
                                                  **region_filter,
                                                  is_active=True).select_related(
        'category',
        'region')

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        'store': store,
        "ads_found": advertisements.count(),
        "category": categories_annotate,
        "category_bread_crumbs": category_bread_crumbs,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        'page_obj': page_obj,
        'date': state_sort_by_date,
        'adaptive_navigation': f"""{store.title}. {category.main_title if
        category.main_title else category.title}. Беларусь"""
    }

    response = render(request, 'store_details.html', context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)
    response.set_cookie('user_auth', request.user.id)

    return response


def get_page_search_result_for_advertisements_in_the_store(request, store_slug):
    """
    Сборка страницы с детальной информацией выбранного магазина
    и результатами поиска по объявлениям этого магазина.
    Модели: Store, Advertisement, Category, Region
    """
    categories = []
    copy_of_request_get = dict.copy(request.GET)

    (order_by,
     sort_for_paginator,
     state_sort_by_date) = setting_values_for_sorting_from_cookie_or_request_get(request.COOKIES, request.GET)
    (category,
     category_bread_crumbs) = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('category',
                                                                                                   None), Category)
    (region,
     region_bread_crumbs) = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('region',
                                                                                                 None), Region)

    query, copy_of_request_get = make_clear_query(request.META.get('QUERY_STRING'), copy_of_request_get)
    field_for_search, search_lookup, field_annotate = forming_fields_for_annotation_and_search(copy_of_request_get)

    search_parameters = setting_search_options(category=category,
                                               region=region,
                                               only_photo=request.GET.get('only_photo'),
                                               only_video=request.GET.get('only_video'),
                                               only_title=request.GET.get('only_title'),
                                               text_search=request.GET.get('text_search'),
                                               field_for_search=field_for_search,
                                               search_lookup=search_lookup)

    store = Store.objects.get(slug=store_slug)

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
                                                                                "store": store,
                                                                                **search_parameters})
        if request.GET.get('category'):
            categories = categories_annotate.filter(parent_id=request.GET.get('category'))
    except Exception as e:
        # Логирование
        print(f"Error fetching categories: {e}")

    advertisements = get_result_for_filter_advertisement_query(search_parameters,
                                                               field_annotate,
                                                               search_lookup,
                                                               order_by=order_by,
                                                               store=store)

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        "ads_found": advertisements.count(),
        "store": store,
        "page_obj": page_obj,
        "region_bread_crumbs": region_bread_crumbs,
        "category_bread_crumbs": category_bread_crumbs,
        "category": categories if request.GET.get('category') else categories_annotate,
        "query": query,
        'date': state_sort_by_date,
        'adaptive_navigation': f'{store.title}. Результаты поиска'
    }
    response = render(request, "stores_search_result_for_advertisement.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


@login_required
@permission_required("store.add_store", raise_exception=True)
def get_page_for_add_new_store(request):
    """
    Сборка страницы для создания нового магазина пользователя.
    Модели: Store, Category, Region, User.
    Формы: StoreForm.
    """
    if request.method == 'POST':
        store_form = StoreForm(request.POST, request.FILES)
        if store_form.is_valid():
            store = store_form.save(commit=False)
            store.user = request.user
            store.save()
            messages.success(request, f"Новый магазин {store} успешно создан!")
            return redirect('my_store')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        store_form = StoreForm(initial={'contact_name': request.user.first_name,
                                        'email': request.user.email,
                                        'phone_num': request.user.phone_number
                                        })

    context = {
        "store_form": store_form,
        "adaptive_navigation": "Добавить магазин"
    }

    return render(request, 'profile_add_store.html', context)


@login_required
@permission_required("store.change_store", raise_exception=True)
def get_page_for_edit_store(request, store_id):
    """
    Сборка страницы для редактирования магазина пользователя.
    Модели: Store, Category, Region.
    Формы: StoreForm.
    """
    store = get_object_or_404(Store, user=request.user, id=store_id)

    if request.method == 'POST':
        edit_selected_store_form = StoreForm(request.POST, request.FILES, instance=store)

        if edit_selected_store_form.is_valid():
            edit_selected_store_form.save()
            messages.success(request, f"Магазин {store} успешно изменён!")
            return redirect('my_store')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        edit_selected_store_form = StoreForm(instance=store)

    context = {
        'store_form': edit_selected_store_form,
        'selected_region': store.region,
        "adaptive_navigation": "Редактирование магазина"
    }
    return render(request, 'profile_edit_shop.html', context)


@login_required
@permission_required("store.delete_store", raise_exception=True)
def get_page_for_delete_store(request, store_id):
    """
    Сборка страницы для подтверждения удаления магазина пользователя.
    Модели: Store
    """
    store = get_object_or_404(Store, user=request.user, id=store_id)

    if request.method == "POST":
        try:
            store.delete()
            messages.success(request, f"Магазин {store} успешно удален!")
        except Exception as e:
            # logger.error(f"Ошибка при удалении магазина: {str(e)}")
            messages.error(request, f"Ошибка при удалении магазина, попробуйте позже")
        return redirect('my_store')

    context = {
        'store': store,
        "adaptive_navigation": "Удаление магазина"
    }
    return render(request, 'delete_store.html', context)


@login_required
@permission_required("store.edit_store", raise_exception=True)
def activate_or_deactivate_selected_store(request):
    """
    Активирует либо деактивирует выбранный магазин.
    Модели: Store
    """
    if request.method == "POST":
        if 'activate' in request.POST and request.POST.get('store').isdigit():
            updated = Store.objects.filter(user=request.user, id=request.POST.get('store')).update(is_active=True)
            if updated:
                messages.success(request, "Магазин успешно активирован!")
            return redirect('my_store')
        if 'deactivate' in request.POST and request.POST.get('store').isdigit():
            updated = Store.objects.filter(user=request.user, id=request.POST.get('store')).update(is_active=False)
            if updated:
                messages.success(request, "Магазин успешно деактивирован!")
            return redirect('my_store')
        return redirect('my_store')
    return redirect('my_store')
