from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Value, Case, When
from django.shortcuts import render, redirect

from advertisement.models import Advertisement
from advertisement.utils import make_clear_query, setting_search_options, get_result_for_filter_advertisement_query
from config import settings
from main.forms import FeedbackForm
from paid_service.forms import PaidForm
from publication.models import Publication
from related_data.models import Category, Region
from related_data.utils import create_variables_for_filter_and_bread_crumbs, forming_fields_for_annotation_and_search
from services.email.message import run_send_email_task_celery
from store.models import Store
from utils.template_paginator import variables_for_paginator


# Create your views here.
@login_required
def get_page_in_personal_account_with_active_advertisements(request):
    """
    Сборка страницы с активными объявлениями пользователя в ЛК.
    Модели: Advertisement.
    Формы: PaidForm
    """
    advertisements = Advertisement.objects.filter(author=request.user,
                                                  is_active=True, moderated=True).select_related('category',
                                                                                                 'region').all().order_by(
        '-date_of_last_activation').defer(
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
    active_advertisements_quantity = advertisements.count()
    inactive_advertisements_quantity = Advertisement.objects.filter(author=request.user, is_active=False).count()

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       20)

    form = PaidForm()

    context = {
        "ads": advertisements,
        "active_ads_quantity": active_advertisements_quantity,
        "inactive_ads_quantity": inactive_advertisements_quantity,
        "page_obj": page_obj,
        "adaptive_navigation": "Мои объявления. Активные объявления",
        'form': form
    }
    return render(request, 'profile_user.html', context)


@login_required
def get_page_in_personal_account_with_search_result_by_user_advertisement(request):
    """
    Сборка страницы с результатами поиска по объявлениям пользователя в ЛК.
    Модели: Advertisement, Region, Category.
    Формы: PaidForm
    """
    copy_of_request_get = dict.copy(request.GET)

    (category,
     category_bread_crumbs) = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('category',
                                                                                                   None),
                                                                           Category)
    (region,
     region_bread_crumbs) = create_variables_for_filter_and_bread_crumbs(copy_of_request_get.pop('region',
                                                                                                 None),
                                                                         Region)

    query, copy_of_request_get = make_clear_query(request.META.get('QUERY_STRING'), copy_of_request_get, request.GET)
    field_for_search, search_lookup, field_annotate = forming_fields_for_annotation_and_search(copy_of_request_get)

    search_parameters = setting_search_options(category=category,
                                               region=region,
                                               only_title=request.GET.get('only_title'),
                                               text_search=request.GET.get('text_search'),
                                               field_for_search=field_for_search,
                                               search_lookup=search_lookup,
                                               id=request.GET.get('id'))

    active = request.GET.get('active')
    if not active:
        advertisements_active = get_result_for_filter_advertisement_query(search_parameters,
                                                                          field_annotate,
                                                                          search_lookup,
                                                                          author=request.user)

        advertisements_inactive = get_result_for_filter_advertisement_query(search_parameters,
                                                                            field_annotate,
                                                                            search_lookup,
                                                                            is_active=False,
                                                                            author=request.user).count()
    else:
        advertisements_active = get_result_for_filter_advertisement_query(search_parameters,
                                                                          field_annotate,
                                                                          search_lookup,
                                                                          author=request.user).count

        advertisements_inactive = get_result_for_filter_advertisement_query(search_parameters,
                                                                            field_annotate,
                                                                            search_lookup,
                                                                            is_active=False,
                                                                            author=request.user)

    page_obj = variables_for_paginator(advertisements_active if not active else advertisements_inactive,
                                       request.GET.get('page'),
                                       20)

    form = PaidForm()
    context = {
        "active_ads_quantity": advertisements_active.count() if not active else advertisements_active,
        "inactive_ads_quantity": advertisements_inactive if not active else advertisements_inactive.count(),
        "page_obj": page_obj,
        "query": query,
        "active": active,
        'adaptive_navigation': f'Результаты поиска. {"Активные объявления" if not active else "Архивые объявления"}',
        'form': form,
    }
    return render(request, 'personal_account_search_results.html', context)


@login_required
def delete_or_archive_selected_ads(request):
    """
    Переводит активные объявления в неактивные и наоборот.
    Модели: Advertisement
    """
    if request.method == "POST":
        # Удаляет выбранные объявления из активных или архивных
        # if 'delete_ads' in request.POST:
        #     selected_ads = request.POST.getlist('ads_checkbox')
        #     Advertisement.objects.filter(author=request.user, id__in=selected_ads).delete()
        #     messages.success(request, "Выбранные объявления удалены!")
        #     return redirect('personal_account')
        # Переводит выбранные объявления из активных в архивные
        if 'archive_ads' in request.POST:
            selected_ads = request.POST.getlist('ads_checkbox')
            Advertisement.objects.filter(author=request.user, id__in=selected_ads).update(is_active=False)
            messages.success(request, "Выбранные объявления перемещены в Архивные!")
            return redirect('personal_account')
        if 'restore_ads' in request.POST:
            selected_ads = request.POST.getlist('ads_checkbox')
            ads_updated_count = Advertisement.objects.filter(author=request.user, id__in=selected_ads, moderated=True,
                                                             date_of_deactivate__date__gte=datetime.now()).update(
                is_active=True)
            if ads_updated_count == len(selected_ads):
                messages.success(request, "Выбранные объявления восстановлены!")
            else:
                messages.success(request, "Не все объявления удалось восстановить!")
            return redirect('inactive_adds')
        return redirect('personal_account')
    return redirect('personal_account')


@login_required
def get_page_in_personal_account_with_inactive_advertisements(request):
    """
    Сборка страницы с активными объявлениями пользователя в ЛК.
    Модели: Advertisement.
    Формы: PaidForm
    """
    advertisements = Advertisement.objects.filter(author=request.user,
                                                  is_active=False
                                                  ).select_related('category',
                                                                   'region').all().order_by(
        '-date_of_last_activation').defer(
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
    inactive_advertisements_quantity = len(advertisements)
    active_advertisements_quantity = Advertisement.objects.filter(author=request.user,
                                                                  is_active=True,
                                                                  moderated=True).count()
    locations = Region.objects.filter(type='Область')
    category_list = Category.objects.filter(level__lte=1)

    page_obj = variables_for_paginator(advertisements,
                                       request.GET.get('page'),
                                       20)

    form = PaidForm()

    context = {
        "ads": advertisements,
        "active_ads_quantity": active_advertisements_quantity,
        "inactive_ads_quantity": inactive_advertisements_quantity,
        "locations": locations,
        "category_list": category_list,
        "page_obj": page_obj,
        "adaptive_navigation": "Мои объявления. Архивные объявления",
        "form": form,
    }
    return render(request, 'inactive_adds.html', context)


@login_required
@permission_required("store.view_store", raise_exception=True)
def get_page_in_personal_account_with_user_stores(request):
    """
    Сборка страницы со всеми магазинами пользователя в ЛК.
    Модели: Store.
    """
    stores = Store.objects.filter(user=request.user).order_by('id')
    context = {
        'stores': stores,
        "adaptive_navigation": "Мои магазины"
    }
    return render(request, 'profile_shop.html', context)


@login_required
@permission_required("publication.view_publication", raise_exception=True)
def get_page_in_personal_account_all_user_publications(request):
    """
    Сборка страницы со всеми публикациями пользователя в ЛК.
    Модели: Publication.
    """
    user_publications = Publication.objects.filter(user=request.user.id).order_by('-date_of_create')
    context = {
        "user_publications": user_publications,
        "adaptive_navigation": "Мои публикации"
    }
    return render(request=request, template_name='profile_publications.html', context=context)


@login_required
def get_user_favorites_page(request):
    """
    Сборка страницы 'Избранное'пользователя в ЛК.
    Модели: Advertisement.
    """
    favorites_list = Advertisement.objects.filter(
        id__in=request.user.userfavorites.favorites,
        is_active=True,
        moderated=True
    ).annotate(
        note=Case(
            *[When(id=ad_id, then=Value(note)) for ad_id, note in
              request.user.userfavorites.notes_for_favorites.items()],
            default=Value("")  # Значение по умолчанию, если заметка не найдена
        )
    )
    context = {
        "favorites_list": favorites_list,
        "adaptive_navigation": "Избранное"
    }
    return render(request, "profile_favorites.html", context)


@login_required
def get_page_send_to_administration_email(request):
    """
    Сборка страницы "Написать администратору".
    Отправка письма администрации сайта
    """
    if request.method == "POST":
        new_feedback_form = FeedbackForm(request.POST)

        if new_feedback_form.is_valid():
            subject = new_feedback_form.cleaned_data.get("subject")
            sender = new_feedback_form.cleaned_data.get("email")
            message = new_feedback_form.cleaned_data.get("message")

            run_send_email_task_celery("Обратная связь",
                                       "asend_feedbeck.html",
                                       settings.EMAIL_HOST_USER,
                                       message=message,
                                       subject=subject,
                                       sender=sender,
                                       )

            messages.success(request, f"Ваше письмо отправлено администрации сайта ")
            return redirect("personal_account")

        feedback_form = FeedbackForm(request.POST)
        feedback_form.errors.update(new_feedback_form.errors)
        context = {
            "feedback_form": feedback_form,
        }
        return render(request, 'profile_send_admin.html', context)

    feedback_form = FeedbackForm()
    context = {
        "feedback_form": feedback_form,
        "adaptive_navigation": "Написать администрации"
    }
    return render(request, 'profile_send_admin.html', context)
