import codecs
import json
import smtplib
from datetime import datetime

import PIL
from django.contrib import messages

from django.contrib.postgres.aggregates import ArrayAgg

from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, F, Count, Func, Value, ExpressionWrapper
from django.db.models.fields.json import KT
from django.db.models.functions import Concat, Length
from django.forms import CharField
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import make_aware

from users.models import User
from advertisement.models import Advertisement, Region, Category, Store, ElementTwo, PhotoAdvertisement, Field, Element
from advertisement.utils import (get_region_variables, sorted_by, sorted_by_number, sorted_by_date_or_price,
                                 variables_for_paginator, where_to_look, search_additional_information,
                                 annotating_field)
from config import settings
from main_page_domer.forms import FeedbackForm
from main_page_domer.models import Help, Publication, AboutOrganization


def get_main_page(request):
    """ Отдаём главную страницу """
    advertisement_queryset = Advertisement.objects.filter(
        is_active=True, moderated=True).select_related(
        'category', 'region').order_by("-date_of_create")[:10].defer(
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
    vip_advertisement = Advertisement.objects.filter(vip=True, active=True, moderated=True)
    context = {
        "advertisement": advertisement_queryset,
        "vip_advertisement": vip_advertisement,
        "adaptive_navigation": "Общебелорусская доска объявлений"
    }
    return render(request, 'main.html', context)


def get_stores_page(request):
    """ Страница со всеми магазинами сайта """
    store_queryset = Store.objects.filter(is_active=True).select_related('category', 'region')
    category_queryset = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                           Store,
                                                           'category',
                                                           'store_counts',
                                                           cumulative=True,
                                                           extra_filters={"is_active": True})
    paginator = Paginator(store_queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "stores_found": store_queryset.count(),
        "category": category_queryset,
        "page_obj": page_obj,
        'adaptive_navigation': 'Магазины. Беларусь'
    }

    return render(request, 'stores.html', context)


def get_store_search(request):
    """ Отдача страницы с результатами поиска по магазинам"""
    text_search = request.GET.get("text_search")

    dict_for_filter = {}
    cop = dict.copy(request.GET)

    category, category_bread_crumbs = where_to_look(cop.pop('category', None), Category)
    region, region_bread_crumbs = where_to_look(cop.pop('region', None), Region)

    query = request.META.get('QUERY_STRING').replace(f'page={request.GET.get("page")}&', '')

    if category:
        dict_for_filter['category__in'] = category
    if text_search:
        dict_for_filter['search_vector'] = cop.pop('text_search')
    if region:
        dict_for_filter['region__in'] = region

    store_queryset = Store.objects.filter(is_active=True, **dict_for_filter).select_related('category', 'region')
    category_queryset = Category.objects.add_related_count(category.get_descendants() if category
                                                           else Category.objects.root_nodes(),
                                                           Store,
                                                           'category',
                                                           'store_counts',
                                                           cumulative=True,
                                                           extra_filters={"is_active": True,
                                                                          **dict_for_filter})

    paginator = Paginator(store_queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "stores_found": store_queryset.count(),
        "category": category_queryset,
        "query": query,
        "page_obj": page_obj,
        'adaptive_navigation': 'Магазины. Результат поиска'
    }

    return render(request, 'stores_search_result.html', context)


def get_stores_by_category(request, category_slug):
    """Переходы по дочерним категориям магазинов """
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))
    category_queryset_all = Category.objects.all()
    category = get_object_or_404(category_queryset_all, slug=category_slug)
    category_queryset_an = Category.objects.add_related_count(category.get_descendants(),
                                                              Store,
                                                              'category',
                                                              'store_counts',
                                                              cumulative=True,
                                                              extra_filters={"region__in": region_filter['region__in'],
                                                                             "is_active": True})
    store_queryset = Store.objects.filter(Q(category__in=category_queryset_an) |
                                                          Q(category__slug=category.slug),
                                                          **region_filter,
                                                          is_active=True).select_related(
                                                          'category',
                                                          'region')
    paginator = Paginator(store_queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "stores_found": store_queryset.count(),
        "category": category_queryset_an,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        "adaptive_navigation": f"Магазины. {category.main_title if category.main_title else category.title}. Беларусь"
    }
    return render(request, 'stores.html', context)


def get_store_by_title(request, store_slug):
    """ Переход на страницу выбранного магазина с его объявлениями """
    order_by = sorted_by(request.COOKIES.get('sorted_by'))
    sort_for_paginator = sorted_by_number(request.COOKIES.get('sort'))
    state_sort_by_date = request.COOKIES.get('date', 0)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    if request.GET.get('date') or request.GET.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(request.GET)
    if request.GET.get('sort'):
        sort_for_paginator = sorted_by_number(request.GET.get('sort'))

    store_page = get_object_or_404(Store, slug=store_slug)
    advertisement_queryset = Advertisement.objects.filter(store=store_page, is_active=True,
                                                          moderated=True, **region_filter).select_related(
                                                          'category',
                                                          'region').order_by(order_by)
    category_queryset = Category.objects.add_related_count(Category.objects.root_nodes(),
                                                           Advertisement,
                                                           'category',
                                                           'advertisement_counts',
                                                           cumulative=True,
                                                           extra_filters={"region__in": region_filter['region__in'],
                                                                          "store": store_page,
                                                                          "is_active": True,
                                                                          "moderated": True
                                                                          })

    page_obj = variables_for_paginator(advertisement_queryset,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        'store': store_page,
        "ads_found": advertisement_queryset.count(),
        "category": category_queryset,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        "page_obj": page_obj,
        'date': state_sort_by_date,
        'adaptive_navigation': f'{store_page.title}. Беларусь'

    }
    response = render(request, 'store_details.html', context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)
    response.set_cookie('user_auth', request.user.id)

    return response


def get_store_by_title_and_category(request, store_slug, category_slug):
    """ Переходы по дочерним категориям объявлений выбранного магазина """
    order_by = sorted_by(request.COOKIES.get('sorted_by'))
    sort_for_paginator = sorted_by_number(request.COOKIES.get('sort'))
    state_sort_by_date = request.COOKIES.get('date', 0)
    region_filter, region_param, region_bread_crumbs = get_region_variables(request.GET.get('region'))

    if request.GET.get('date') or request.GET.get('price'):
        state_sort_by_date, order_by = sorted_by_date_or_price(request.GET)
    if request.GET.get('sort'):
        sort_for_paginator = sorted_by_number(request.GET.get('sort'))

    store_page = get_object_or_404(Store, slug=store_slug)
    category_queryset_all = Category.objects.all()
    category = get_object_or_404(category_queryset_all, slug=category_slug)
    category_bread_crumbs = category.get_ancestors(ascending=False, include_self=True)
    category_queryset_an = Category.objects.add_related_count(category.get_descendants(),
                                                              Advertisement,
                                                              'category',
                                                              'advertisement_counts',
                                                              cumulative=True,
                                                              extra_filters={
                                                                  "region__in": region_filter['region__in'],
                                                                  "store": store_page,
                                                                  "is_active": True,
                                                                  "moderated": True
                                                              })
    category_queryset = category_queryset_an.filter(parent_id=category.id)
    advertisement_queryset = Advertisement.objects.filter(Q(category__in=category_queryset_an) |
                                                          Q(category__slug=category.slug),
                                                          store=store_page,
                                                          **region_filter,
                                                          is_active=True).select_related(
                                                          'category',
                                                          'region')

    page_obj = variables_for_paginator(advertisement_queryset,
                                       request.GET.get('page'),
                                       sort_for_paginator)

    context = {
        'store': store_page,
        "ads_found": advertisement_queryset.count(),
        "category": category_queryset,
        "category_bread_crumbs": category_bread_crumbs,
        "region_bread_crumbs": region_bread_crumbs,
        "region_param": region_param,
        'page_obj': page_obj,
        'date': state_sort_by_date,
        'adaptive_navigation': f'{store_page.title}. {category.main_title if category.main_title else category.title}. Беларусь'

    }

    response = render(request, 'store_details.html', context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)
    response.set_cookie('user_auth', request.user.id)

    return response


def search_for_advertisements_in_the_store(request, store_slug):
    search_parameters = {}
    search_parameters_only = {}
    category_queryset_an = []
    key_delete = ['page', 'sort', 'date', 'price', 'text_search', 'only_video']
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
    if request.GET.get('only_title') and request.GET.get('text_search'):
        search_parameters['search_title_vector'] = request.GET.get('text_search')
        cop.pop('only_title')
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

    store_page = Store.objects.get(slug=store_slug)

    try:
        category_queryset_an = Category.objects.add_related_count(category.get_descendants(),
                                                                  Advertisement,
                                                                  'category',
                                                                  'advertisement_counts',
                                                                  cumulative=True,
                                                                  extra_filters={"is_active": True,
                                                                                 "moderated": True,
                                                                                 "store": store_page,
                                                                                 **search_parameters})
    except:
        pass

    if search_q:
        search_parameters.update(search_q)

    advertisement_queryset = Advertisement.objects.annotate(**{key: KT(value) for key, value in search_annotate.items()}
                                                            ).filter(is_active=True,
                                                                     moderated=True,
                                                                     store=store_page,
                                                                     **search_parameters
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
        "store": store_page,
        "page_obj": page_obj,
        "region_bread_crumbs": region_bread_crumbs,
        "category_bread_crumbs": category_bread_crumbs,
        "category": category_queryset_an,
        "query": query,
        'date': state_sort_by_date,
        'adaptive_navigation': f'{store_page.title}. Результаты поиска'
    }
    response = render(request, "stores_search_result_for_advertisement.html", context)
    response.set_cookie('sort', sort_for_paginator)
    response.set_cookie('date', state_sort_by_date)
    response.set_cookie('sorted_by', order_by)

    return response


def get_site_map_page(request):
    # category_queryset = Category.objects.add_related_count(Category.objects.all(),
    #                                                        Advertisement,
    #                                                        'category',
    #                                                        'advertisement_counts',
    #                                                        cumulative=True,
    #                                                        extra_filters={"is_active": True,
    #                                                                       "moderated": True
    #                                                                       })
    #
    # category_queryset = Category.objects.add_related_count(Category.objects.all(),
    #                                                        Field,
    #                                                        'category',
    #                                                        'element_counts',
    #                                                        cumulative=True,
    #                                                        extra_filters={"is_active": True,
    #                                                                       "moderated": True
    #                                                                       })


    # print(category_queryset)





    category_list = Category.objects.prefetch_related('field_set__spisok__element_set', 'field_set')
                                                      # ).annotate(element=(ArrayAgg(F('field__spisok__element'))))




    # elements = Element.objects.alias(spisok__field_set__category__advertisement_set__additional_information

    # element = Element.objects.annotate(field=F('spisok__field__title')).annotate(adver=Count(F(f'spisok__field__category__advertisement__additional_information__{field}__contains'))).filter(adver__gt=1)
    #
    # print(element)
    #
    # for e in element:
    #
    #     print(e.adver)
    # .filter(spisok__field__category__advertisement__additional_information_view2__values__contains=[])
    # Concat(Value("["), 'title', Value(", "), 'elementtwo__title', Value("]")) if F('elementtwo') else
    # elements = Element.objects.annotate(two=Length('elementtwo__title'))
    # .filter(spisok__field__category__advertisement__additional_information_view2__values__contains=F('two'))

    # elements = Element.objects.exclude(elementtwo__title__exact=None
    #                                    ).annotate(two=Concat('title', Value(", "), 'elementtwo__title'))
    #                                               # ).annotate(two=ArrayAgg(F('two2'))
    #                                               #             )
    # elements2 = Element.objects.filter(elementtwo__title__exact=None
    #                                    ).annotate(two=F('title'))

    # count = 0
    # for e in elements2:
    #     print(count, e)
    #     count += 1

    # x = [e.two for e in elements] + [e.two for e in elements2]

    # elements3 = Element.objects.filter(spisok__field__category__advertisement__additional_information_view2__values__overlap=x).values('id','title','spisok__field__category' ).distinct('title')
    # elements4 = Element.objects.filter(spisok__field__category__advertisement__additional_information_view2__values__overlap=).distinct('title').count()

    # print(elements3)
    # for e in elements3:
    #     print(e)
    # print(elements4)

    # advertisement = Advertisement.objects.filter(category_id=4, additional_information_view2__values__contains=['Audi, 80'])
    # advertisement = Advertisement.objects.filter(category_id=4, additional_information_view__contains=['Марка, модель', 'Audi, 80'])
    # print(advertisement[0].additional_information_view)
    # print(advertisement)
    # field = Field.objects.alias(f'category__advertisement_set__additional_information_')
    # advertisement = Advertisement.objects.all()
    # for a in advertisement:
    #     a.additional_information_view2 = {key: value for key, value in a.additional_information_view}
    #     a.save()

    context = {
        # 'nodes': category_queryset,
        'nodes': category_list,
        # 'elements': elements3
    }

    return render(request, 'map.html', context)


def get_publications(request):
    """ Страница с всеми публикациями """
    publications = Publication.objects.exclude(moderated=False).order_by('date_of_create')

    page_obj = variables_for_paginator(publications,
                                       request.GET.get('page'),
                                       10)

    context = {
        'publications_count': publications.count(),
        'publications': page_obj,
        'adaptive_navigation': 'Публикации. Беларусь'
    }
    return render(request, 'publications.html', context)


def get_publication_by_slug(request, slug):
    """ Страница публикации по slug """
    Publication.objects.filter(slug=slug).update(counter_views=F('counter_views')+1)
    publication = get_object_or_404(Publication, slug=slug, moderated=True)
    context = {
        'publication': publication,
        'adaptive_navigation': f'{publication.title}'
    }
    return render(request, 'publication_by_slug.html', context)


def publication_search_result(request):
    """ Страница с результатами поиска по публикациям """
    search_parameters = {}
    search_parameters_only = {}
    cop = dict.copy(request.GET)

    if request.GET.get('only_title') and request.GET.get('text_search'):
        search_parameters['search_title_vector'] = request.GET.get('text_search')
        cop.pop('only_title')
    elif request.GET.get('text_search'):
        search_parameters['search_vector'] = request.GET.get('text_search')

    query = request.META.get('QUERY_STRING').replace(f'page={request.GET.get("page")}&', '')

    publications = Publication.objects.filter(moderated=True, **search_parameters
                                              ).exclude(**search_parameters_only
                                                        ).order_by('date_of_create')

    page_obj = variables_for_paginator(publications,
                                       request.GET.get('page'),
                                       10)

    context = {
        'publications_count': publications.count(),
        'publications': page_obj,
        'query': query,
        'adaptive_navigation': 'Публикации. Результаты поиска'
    }
    return render(request, 'publication_search_result.html', context)


def get_feedback_page(request):
    """ Страница связи с администрацией сайта """
    if request.method == "POST":
        new_feedback_form = FeedbackForm(request.POST)

        if new_feedback_form.is_valid():
            subject = f'"{new_feedback_form.cleaned_data.get("subject")}" от пользователя {new_feedback_form.cleaned_data.get("email")}'
            message = new_feedback_form.cleaned_data.get("message")

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
            except smtplib.SMTPException as error:
                return render(request, 'feedback.html',
                              {'feedback_form': new_feedback_form, 'error_message': str(error)})

            messages.success(request, f"Ваше письмо отправлено администрации сайта ")
            return redirect("feedback")

        feedback_form = FeedbackForm(request.POST)
        feedback_form.errors.update(new_feedback_form.errors)
        context = {
            "feedback_form": feedback_form,
        }
        return render(request, 'feedback.html', context)

    feedback_form = FeedbackForm()
    context = {
        "feedback_form": feedback_form,
    }
    return render(request, 'feedback.html', context)


def get_help_page(request):
    help = Help.objects.first()
    context = {
        "help": help,
    }
    return render(request, "help_page.html", context)



#======================================================================================================================
def desc_and_opis(objavl):
    o = objavl.get("opis").split('<hr>')
    ad_info = {}
    for i in o[0].split('\n'):
        if i != objavl.get('zag') and i != '':
            a = i.split(": ")
            if a[0] == 'Марка, модель':
                while a[1][0] == ' ':
                    a[1] = a[1].replace(' ', '', 1)
                ad_info[a[0]] = a[1].replace(" ", ", ", 1)
            elif a[0] == 'Этаж':
                while a[1][0] == ' ':
                    a[1] = a[1].replace(' ', '', 1)
                ad_info[a[0]] = a[1].replace("/", ", ", 1)
            else:
                if len(a[1].split(" ")) > 1:
                    f = ElementTwo.objects.filter(element_id__spisok_id__field__category_id=objavl.get('id_catalog'),
                                                  title__contains=a[1].split(' ')[-1])
                    if 'gt' in a[1] or 'lt' in a[1]:
                        f = ElementTwo.objects.filter(
                            element_id__spisok_id__field__category_id=objavl.get('id_catalog'),
                            title__contains=f"{a[1].split(' ')[-2]} {a[1].split(' ')[-1]}")
                    if f:
                        for x in f:
                            if x.title in a[1]:
                                a[1] = a[1].removesuffix(x.title)
                                while a[1][-1] == " ":
                                    a[1] = a[1].removesuffix(' ')
                                a[1] = f"{a[1]}, {x.title}"
                                print(a[1])
                                break
                while a[1][0] == ' ':
                    a[1] = a[1].replace(' ', '', 1)
                ad_info[a[0]] = a[1]

    return ad_info


def download_advertis(request):
    with codecs.open('./new_board.json', 'r', 'utf-8') as json_file:
        ishod_dump = json.loads(json_file.read())
        for advertis in ishod_dump:

            new_advertis = Advertisement(author=User.objects.get(id=advertis.get("id_akk")) if advertis.get("id_akk") else None,
            article= None,
            title= advertis.get("zag"),
            price= advertis.get("f_cena_"),
            category= Category.objects.get(id=advertis.get("id_catalog")),
            bearer= "Частное лицо" if advertis.get("pols") == "1" else "Компания",
            region= Region.objects.get(id=advertis.get("id_gorod")),
            preview_image= advertis.get('small').replace('\\', '').replace('s','b') if advertis.get('small') else None,
            counter_views= advertis.get("counter"),
            contact_name= advertis.get("contakt"),
            phone_num= advertis.get("tel").replace(" ", "").replace("-", ""),
            email= advertis.get("email"),
            store= None,
                                         date_of_create=make_aware(
                                             datetime.strptime(advertis.get("data"), "%Y-%m-%d %H:%M:%S")),
                                         date_of_deactivate=make_aware(
                                             datetime.strptime(advertis.get("data1"), "%Y-%m-%d %H:%M:%S")),
            moderated= True,
            is_active= True,
            vip= False,
            highlight_ad= False,
            special_accommodation= False,
            raise_in_search= False,
            additional_information= desc_and_opis(advertis),
            description= advertis.get("opis").split('<hr>')[1],
            video_link= advertis.get("video_link"))

            # new_advertis.save()

    return render(request, "download_adver.html")



def dowload_user(request):
    # with codecs.open('./akk.json', 'r', 'utf-8') as json_file:
    #     ishod_dump = json.loads(json_file.read())
    #     for i in ishod_dump:
    #         User.objects.create_user(
    #             email=i.get('email'),
    #             first_name=i.get('contakt'),
    #             phone_number=i.get('tel').replace(' ', ''),
    #             date_joined=i.get('data'),
    #             password=i.get('pass')
    #         )
#========================download store==================================================
    # with codecs.open('./new_id_store.json', 'r', 'utf-8') as json_file:
    #     ishod_dump = json.loads(json_file.read())
    #
    #     for store in ishod_dump:
    #
    #         new_store=Store(
    #             region=Region.objects.get(id=store.get('id_gorod')),
    #             title=store["zag"],
    #             slug=store.get('zag_url'),
    #             description=store.get('opis'),
    #             contact_name=store.get('contakt'),
    #             email=store.get('email'),
    #             phone_num=store.get('tel'),
    #             video_link=store.get('video_link'),
    #             logo_image=f'images/store_img/{store.get("small").split("/")[1]}' if store.get("small") else None,
    #             date_of_create=make_aware(datetime.strptime(store.get("data"), "%Y-%m-%d %H:%M:%S")),
    #             user=User.objects.get(id=store.get('id_akk')),
    #             is_active=1 if store.get('activ') == "0" else 0,
    #             category=Category.objects.get(id=store.get('category_id')),
    #             url=store.get('url_real'),
    #             address=store.get('adres'),
    #         )
    #         new_store.save()

    return render(request, 'download_adver.html')







def dowload_photo(request):
    with codecs.open('./foto_07_07_2024.json', 'r', 'utf-8') as json_file:
        ishod_dump = json.loads(json_file.read())
        with codecs.open('./new_id_board.json', 'r', 'utf-8') as json_file:
            advertis_id = json.loads(json_file.read())
        for i in ishod_dump:
            paths = f'foto/{i.get("papka")}/{i.get("id_foto")}b.jpg'
            try:
                with codecs.open(f"./media/{paths}", 'r') as file:
                    pass
            except FileNotFoundError:
                print("файл не неайден", paths)
            except PIL.UnidentifiedImageError:
                print("файл не неайден",paths)
            else:
                advertis = Advertisement.objects.get(id=advertis_id.get(i.get("id")))
                photo = PhotoAdvertisement(photo=paths, advertisement_id=advertis.id)
                photo.save()

    return render(request, 'download_adver.html')


# def page_not_found(request, exception):
def page_not_found(request):
    '''отдает страничку с ошибкой 404'''
    return render(request, '404.html', status=404)
