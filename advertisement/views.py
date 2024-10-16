import codecs
import json
from pprint import pprint
from django.db.models import Q
import random
from datetime import datetime, timedelta
from django.db.models import Q, F
from django.db.models.fields.json import KT
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import get_current_timezone

from main_page_domer.forms import ComplaintForm
from main_page_domer.models import ReasonOfComplaint

from .models import Advertisement, Category, Region, Spisok, Element, ElementTwo, Field,  BadWords, ErrorFile
from .tasks import save_many_ads_from_zip_task, save_many_ads_from_excel_task
from .utils import sorted_by_number, variables_for_paginator, sorted_by_date_or_price, sorted_by, \
    get_region_variables, where_to_look, search_additional_information, annotating_field
from .forms import UploadFileForm
from .models import UploadFile
import openpyxl
from zipfile import ZipFile


def get_advertisement_page(request):
    order_by = sorted_by(request.COOKIES.get('sorted_by'))
    sort_for_paginator = sorted_by_number(request.COOKIES.get('sort'))
    state_sort_by_date = request.COOKIES.get('date', 0)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    if request.GET.get('date') or request.GET.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(request.GET)
    if request.GET.get('sort'):
        sort_for_paginator = sorted_by_number(request.GET.get('sort'))


    advertisement_queryset = Advertisement.objects.filter(is_active=True,
                                                          moderated=True,
                                                          **region_filter).select_related(
        'category',
        'region'
    ).order_by("-raise_in_search", order_by).defer(
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
    vip_advertisement = advertisement_queryset.filter(vip=True, is_active=True, moderated=True)
    category_queryset = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                           Advertisement,
                                                           'category',
                                                           'advertisement_counts',
                                                           cumulative=True,
                                                           extra_filters={"region__in": region_filter['region__in'],
                                                                          "is_active": True,
                                                                          "moderated": True})

    page_obj = variables_for_paginator(advertisement_queryset,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        "ads_found": advertisement_queryset.count(),
        "category": category_queryset,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        "vip_advertisement": vip_advertisement,
        'date': state_sort_by_date,
        'adaptive_navigation': "Доска объявлений. Беларусь",
    }

    response = render(request, "advertisementAdd.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)
    response.set_cookie('user_auth', request.user.id)

    return response


def get_advertisement_by_category(request, category_slug):
    order_by = sorted_by(request.COOKIES.get('sorted_by'))
    sort_for_paginator = sorted_by_number(request.COOKIES.get('sort'))
    state_sort_by_date = request.COOKIES.get('date', 0)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    if request.GET.get('date') or request.GET.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(request.GET)
    if request.GET.get('sort'):
        sort_for_paginator = sorted_by_number(request.GET.get('sort'))

    category_queryset_all = Category.objects.all()
    category = get_object_or_404(category_queryset_all, slug=category_slug)
    category_bread_crumbs = category.get_ancestors(ascending=False, include_self=True)
    category_queryset_an = Category.objects.add_related_count(category.get_descendants(),
                                                              Advertisement,
                                                              'category',
                                                              'advertisement_counts',
                                                              cumulative=True,
                                                              extra_filters={"region__in": region_filter['region__in'],
                                                                             "is_active": True,
                                                                             "moderated": True})
    category_queryset = category_queryset_an.filter(parent_id=category.id)
    advertisement_queryset = Advertisement.objects.filter(Q(category__in=category_queryset_an) |
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
    vip_advertisement = advertisement_queryset.filter(vip=True, is_active=True, moderated=True)
    page_obj = variables_for_paginator(advertisement_queryset,
                                       request.GET.get('page'),
                                       sort_for_paginator)
    context = {
        "ads_found": advertisement_queryset.count(),
        "category": category_queryset,
        "region_param": region_param,
        "category_bread_crumbs": category_bread_crumbs,
        "region_bread_crumbs": region_bread_crumbs,
        "page_obj": page_obj,
        "vip_advertisement": vip_advertisement,
        'date': state_sort_by_date,
        'adaptive_navigation': f"{category.main_title if category.main_title else category.title}. Беларусь",
    }

    response = render(request, "advertisementAdd.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


def get_page_place_an_ad(request):
    category_list = Category.objects.filter(level__lte=1)
    oblast = Region.objects.filter(level=0)
    categories = Category.objects.filter(level=0)

    context = {
        "category_list": category_list,
        'adaptive_navigation': "Добавление объявления",
        'oblast': oblast,
        'categories': categories,
    }

    return render(request, 'place_an_ad.html', context)


def get_page_place_an_favorites(request):
    context = {}
    category_list = Category.objects.filter(level__lte=1)
    context["category_list"] = category_list
    json_data = request.GET.get('list')
    data = json.loads(json_data)

    if len(data):
        objects = Advertisement.objects.filter(pk__in=data)
        context['objects'] = objects
        context['cards_num'] = len(objects)

    return render(request, 'place_an_favorites.html', context)


# @cache_page(60 * 15)
def get_advertisement_details_page(request, slug):
    '''Отдаем страничку с детальным описанием объявления'''
    advertisement_main = get_object_or_404(Advertisement.objects.prefetch_related("photoadvertisement_set"), slug=slug)
    Advertisement.objects.filter(id=advertisement_main.id).update(counter_views=F("counter_views") + 1)
    category_crumbs = advertisement_main.category.get_ancestors(ascending=False, include_self=True)
    date = datetime.now(tz=get_current_timezone()) - timedelta(days=50)
    similar_advertisement = list(Advertisement.objects.filter(moderated=True,
                                                         is_active=True,
                                                         category_id=advertisement_main.category,
                                                         date_of_create__date__gte=date
                                                         ).exclude(id=advertisement_main.id).values_list('id',
                                                                                                         flat=True))

    similar_advertisement = random.sample(similar_advertisement,
                                          4 if len(similar_advertisement) >= 4 else len(similar_advertisement))
    similar_advertisement = Advertisement.objects.filter(id__in=similar_advertisement)
    reason_of_complaint = ReasonOfComplaint.objects.all()
    form = ComplaintForm()
    context = {
        "advertisement": advertisement_main,
        "category_crumbs": category_crumbs,
        "similar_advertisement": similar_advertisement,
        "reason_list": reason_of_complaint,
        "form": form,
        "adaptive_navigation": f"{advertisement_main.title}.",
    }
    return render(request=request,
                  template_name='advertisement_details.html',
                  context=context)


def editing_an_ad(request, id):
    advertisement = Advertisement.objects.get(id=id)

    region = Region.objects.all()
    oblast = region.filter(level=0)
    selected_oblast = region.get(id=advertisement.region.parent_id)
    cities = advertisement.region.get_siblings(include_self=True)
    family_categories = advertisement.category.get_family()

    list_categories = [category.get_siblings(include_self=True) for category in family_categories]
    categories = {key: value for key, value in zip(family_categories, list_categories)}

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
    return render(request, 'editing_an_ad.html', context)


def search_result(request):
    search_parameters = {}
    search_parameters_only = {}
    category_queryset_an = []
    key_delete = ['page', 'sort', 'date', 'price', 'text_search','only_title']
    cop = dict.copy(request.GET)

    sort_for_paginator = sorted_by_number(request.COOKIES.get('sort'))
    order_by = sorted_by(request.COOKIES.get('sorted_by'))
    state_sort_by_date = request.COOKIES.get('date', 0)
    category, category_bread_crumbs = where_to_look(cop.pop('category', None), Category)
    region, region_bread_crumbs = where_to_look(cop.pop('region', None), Region)

    if request.GET.get('date') or request.GET.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(request.GET)
    if request.GET.get('sort'):
        sort_for_paginator = sorted_by_number(request.GET.get('sort'))

    if category:
        search_parameters['category__in'] = category
    if region:
        search_parameters['region__in'] = region
    if request.GET.get('only_photo'):
        search_parameters_only['preview_image__exact'] = ''
        cop.pop('only_photo')
    if request.GET.get('only_video'):
        search_parameters_only['video_link__exact'] = ''
        cop.pop('only_video')
    if request.GET.get('only_title') and request.GET.get('text_search'):
        search_parameters['search_title_vector'] = request.GET.get('text_search')
    elif request.GET.get('text_search'):
        search_parameters['search_vector'] = request.GET.get('text_search')

    query = request.META.get('QUERY_STRING')
    for key in key_delete:
        cop.pop(key, None)
        query = query.replace(f'{key}={request.GET.get(key)}&', '')

    try:
        fields = Field.objects.filter(id__in=cop.keys())
    except ValueError:
        raise Http404()

    search, search_kt = search_additional_information(fields, cop)
    search_q, search_annotate = annotating_field(search_kt)

    if search:
        search_parameters['additional_information__contains'] = search

    try:
        category_queryset = Category.objects.add_related_count(category.get_descendants() if
                                                                  category else
                                                                  Category.objects.root_nodes(),
                                                                  Advertisement,
                                                                  'category',
                                                                  'advertisement_counts',
                                                                  cumulative=True,
                                                                  extra_filters={"is_active": True,
                                                                                 "moderated": True,
                                                                                 **search_parameters})
        if request.GET.get('category'):
            category_queryset_an = category_queryset.filter(parent_id=request.GET.get('category'))
    except:
        pass

    if search_q:
        search_parameters.update(search_q)

    advertisement_queryset = Advertisement.objects.annotate(**{key: KT(value) for key, value in search_annotate.items()}
                                                            ).filter(is_active=True, moderated=True, **search_parameters
                                                                     ).exclude(**search_parameters_only
                                                                               ).select_related('category', 'region'
                                                                                                ).order_by(
                                                                                                    "-raise_in_search",
                                                                                                    order_by)

    page_obj = variables_for_paginator(advertisement_queryset,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        "ads_found": advertisement_queryset.count(),
        "page_obj": page_obj,
        "region_bread_crumbs": region_bread_crumbs,
        "category_bread_crumbs": category_bread_crumbs,
        "category": category_queryset_an if request.GET.get('category') else category_queryset,
        "query": query,
        'date': state_sort_by_date,
        'adaptive_navigation': 'Результаты поиска'
    }
    response = render(request, "advertisementSearchResult.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response



def get_bulk_import_of_ads(request):
    """Страница массового импорта объявлений"""
    context = {
        'form': UploadFileForm(),
    }
    file = ErrorFile.objects.filter(user=request.user).last()

    if file != None and file.status == False:
        path = file.file[2:]
        context['file'] = f'http://127.0.0.1:8000//{path}'
        context['error'] = True
        context['answer_error'] = 'Во время последней загрузки файлов несколько объявлений не были сохранены. Чтобы посмотреть объявления с ошибками скачайте файл.'

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data.get("file").name.endswith('xlsx'):
                '''Работа с электронной таблицей'''
                try:
                    uploud_file = form.cleaned_data.get("file")
                    book = openpyxl.open(uploud_file,read_only=True)
                    save_file = UploadFile(file=uploud_file, user=request.user)
                    save_file.save()
                    ads = save_many_ads_from_excel_task.delay(uploud_file=f'./media/{save_file.file.name}',
                                                              id=request.user.id,
                                                              first_name=request.user.first_name,
                                                              phone_number=request.user.phone_number,
                                                              email=request.user.email)

                    save_file.delete()
                    if file != None and file.status == False:
                        file.status = True
                        file.save(update_fields=["status"])
                    result = ads.get()
                    if result != True:
                        path = result.get('file')[1][1:]
                        context['answer_error'] = 'Несколько объявлений не были сохранены. Чтобы посмотреть объявления с ошибками скачайте файл.'
                        context['file'] = f'http://127.0.0.1:8000//{path}'
                        context['error'] = True
                    else:
                        context['answer'] = 'Объявления успешно сохранены'
                        context['error'] = False
                except:
                    context['answer'] = 'Невозможно прочитать файл.'
                    context['error'] = False
            elif form.cleaned_data.get("file").name.endswith('zip'):
                '''Работа с электронным архивом'''
                try:
                    uploud_zip = form.cleaned_data.get("file")
                    with ZipFile(uploud_zip,'r') as zip:
                        files_from_zip = zip.namelist()
                    save_zip = UploadFile(file=uploud_zip, user=request.user)
                    save_zip.save()
                    ads = save_many_ads_from_zip_task.delay(uploud_zip=f'./media/{save_zip.file.name}',
                                                            id=request.user.id,
                                                            first_name=request.user.first_name,
                                                            phone_number=request.user.phone_number,
                                                            email=request.user.email)
                    save_zip.delete()
                    if file != None and file.status == False:
                        file.status = True
                        file.save(update_fields=["status"])
                    result = ads.get()
                    if result != True:
                        path = result.get('file')[1][1:]
                        context['answer_error'] = 'Несколько объявлений не были сохранены. Чтобы посмотреть объявления с ошибками скачайте файл.'
                        context['file'] = f'http://127.0.0.1:8000//{path}'
                        context['error'] = True
                    else:
                        context['answer'] = 'Объявления успешно сохранены'
                        context['error'] = False
                except:
                    context['answer'] = 'Невозможно прочитать файл'
                    context['error'] = False
        else:
            context['answer'] = 'Ошибка при загрузке файла. Убедитесь, что загружаемый файл необходимого расширения'
    else:
        form = UploadFileForm()
    return render(request=request,
                  template_name='bulk_import_ads.html',
                  context = context)


def get_instructions_for_bulk_import_of_ads(request):
    '''функция, которая отдает страницу с инструкцией по массовому импорту объявлений'''
    oblast = Region.objects.filter(level=0)
    categories = Category.objects.filter(level=0)
    context = {
        'oblast': oblast,
        'categories': categories,
    }
    return render(request=request,
                  template_name='instructions_for_bulk_import_of_ads.html',
                  context=context)

# def import_words(request):
#     # with open('./advertisement/r_word.txt', "r") as file:
#     #     for line in file:
#     #         print(line, end='')
#     #         BadWords.objects.create(word=line[0:-1].lower())
#     ad = Advertisement.objects.get(id=1)
#     print(ad)
#     ad.title = "хуй"
#     print(ad)
#     ad.save()
#     return render(request, template_name='import_words.html')


