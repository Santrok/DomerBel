from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count, Min, Max
from django.db.models.fields.json import KT
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from advertisement.forms import StoreForm
from advertisement.models import Region, Category, Advertisement, Store, Field
from advertisement.utils import where_to_look, search_additional_information, \
    annotating_field, variables_for_paginator
from paid_service.forms import PaidForm
from .models import User, Chat, Message

from main_page_domer.models import PhotoPublication, Publication, photo_publications_delete
from .forms import PublicationForm, EditContactDataForm, ChangePasswordForm, MessageForm


@login_required
def get_personal_account_page(request):
    """ Выводит все активные объявления пользователя в ЛК"""
    ads = Advertisement.objects.filter(author=request.user, is_active=True, moderated=True).select_related('category',
                                                                                           'region').all().order_by(
        '-date_of_create').defer(
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
    active_ads_quantity = ads.count()
    inactive_ads_quantity = Advertisement.objects.filter(author=request.user, is_active=False).count()

    paginator = Paginator(ads, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    form = PaidForm()

    context = {
        "ads": ads,
        "active_ads_quantity": active_ads_quantity,
        "inactive_ads_quantity": inactive_ads_quantity,
        "page_obj": page_obj,
        "adaptive_navigation": "Мои объявления. Активные объявления",
        'form': form
    }
    return render(request, 'profile_user.html', context)


@login_required
def search_of_ads_in_personal_account(request):
    """ Поиск среди объявлений пользователя в личном кабинете """
    search_parameters = {}
    key_delete = ['text_search', 'id', 'page', 'active']
    cop = dict.copy(request.GET)

    category, category_bread_crumbs = where_to_look(cop.pop('category', None), Category)
    region, region_bread_crumbs = where_to_look(cop.pop('region', None), Region)

    if category:
        search_parameters['category__in'] = category
    if region:
        search_parameters['region__in'] = region
    if request.GET.get('only_title') and request.GET.get('text_search'):
        search_parameters['search_title_vector'] = request.GET.get('text_search')
        cop.pop('only_title')
    elif request.GET.get('text_search'):
        search_parameters['search_vector'] = request.GET.get('text_search')
    if request.GET.get('id'):
        search_parameters['id'] = request.GET.get('id')

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
    if search_q:
        search_parameters.update(search_q)

    active = request.GET.get('active')
    if not active:
        advertisement_queryset = Advertisement.objects.annotate(
            **{key: KT(value) for key, value in search_annotate.items()}
            ).filter(author=request.user,
                     is_active=True,
                     moderated=True,
                     **search_parameters
                     ).select_related('category', 'region'
                                      ).order_by('-date_of_create')

        advertisement_queryset_inactive = Advertisement.objects.annotate(
            **{key: KT(value) for key, value in search_annotate.items()}
            ).filter(author=request.user,
                     is_active=False,
                     moderated=True,
                     **search_parameters
                     ).count()
    else:
        advertisement_queryset = Advertisement.objects.annotate(
            **{key: KT(value) for key, value in search_annotate.items()}
        ).filter(author=request.user,
                 is_active=True,
                 moderated=True,
                 **search_parameters
                 ).count()

        advertisement_queryset_inactive = Advertisement.objects.annotate(
            **{key: KT(value) for key, value in search_annotate.items()}
        ).filter(author=request.user,
                 is_active=False,
                 moderated=True,
                 **search_parameters
                 ).select_related('category', 'region'
                                  ).order_by('-date_of_create')

    page_obj = variables_for_paginator(advertisement_queryset if not active else advertisement_queryset_inactive,
                                       request.GET.get('page'),
                                       20)

    form = PaidForm()
    context = {
        "active_ads_quantity": advertisement_queryset.count() if not active else advertisement_queryset,
        "inactive_ads_quantity": advertisement_queryset_inactive if not active else advertisement_queryset_inactive.count(),
        "page_obj": page_obj,
        "query": query,
        "active": active,
        'adaptive_navigation': f'Результаты поиска. {"Активные объявления" if not active else "Архивые объявления"}',
        'form': form,
    }
    return render(request, 'personal_account_search_results.html', context)


@login_required
def get_personal_account_inactive_adds_page(request):
    """ Выводит все неактивные объявления пользователя в ЛК"""
    ads = Advertisement.objects.filter(author=request.user, is_active=False).select_related('category',
                                                                                            'region').all().order_by(
        '-date_of_create').defer(
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
    inactive_ads_quantity = len(ads)
    active_ads_quantity = Advertisement.objects.filter(author=request.user, is_active=True, moderated=True).count()
    locations = Region.objects.filter(type='Область')
    category_list = Category.objects.filter(level__lte=1)

    paginator = Paginator(ads, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = PaidForm()

    context = {
        "ads": ads,
        "inactive_ads_quantity": inactive_ads_quantity,
        "active_ads_quantity": active_ads_quantity,
        "locations": locations,
        "category_list": category_list,
        "page_obj": page_obj,
        "adaptive_navigation": "Мои объявления. Архивные объявления",
        "form": form,
    }
    return render(request, 'inactive_adds.html', context)


@login_required
def delete_or_archive_selected_ads(request):
    if request.method == "POST":
        # Удаляет выбранные объявления из активных или архивных
        # if 'delete_ads' in request.POST:
        #     selected_ads = request.POST.getlist('ads_checkbox')
        #     Advertisement.objects.filter(author=request.user, id__in=selected_ads).delete()
        #     messages.success(request, "Выбранные объявления удалены!")
        #     return redirect('users:personal_account')
        # Переводит выбранные объявления из активных в архивные
        if 'archive_ads' in request.POST:
            selected_ads = request.POST.getlist('ads_checkbox')
            Advertisement.objects.filter(author=request.user, id__in=selected_ads).update(is_active=False)
            messages.success(request, "Выбранные объявления перемещены в Архивные!")
            return redirect('users:personal_account')
        if 'restore_ads' in request.POST:
            selected_ads = request.POST.getlist('ads_checkbox')
            ads_updated_count = Advertisement.objects.filter(author=request.user, id__in=selected_ads, moderated=True,
                                                             date_of_deactivate__date__gte=datetime.now()).update(
                is_active=True)
            if ads_updated_count == len(selected_ads):
                messages.success(request, "Выбранные объявления восстановлены!")
            else:
                messages.success(request, "Не все объявления удалось восстановить!")
            return redirect('users:inactive_adds')
        return redirect('users:personal_account')


@login_required
def get_user_data_page(request):
    """ Обрабатывает в личном кабинете две формы на изменение контактных данных и пароля пользователя """
    user = request.user
    edit_contact_data_form = EditContactDataForm(instance=user)
    change_pass_form = ChangePasswordForm()
    if request.method == "POST":
        # Изменение контактных данных пользователя
        if 'edit_contact_data' in request.POST:
            edit_contact_data_form = EditContactDataForm(request.POST, instance=user)
            if edit_contact_data_form.is_valid():
                edit_contact_data_form.save()
                messages.success(request, "Ваши контактные данные успешно изменены!")
                return redirect('users:user_data')
        # Изменение пароля пользователя
        elif 'change_password' in request.POST:
            change_pass_form = ChangePasswordForm(request.POST, instance=user)
            if change_pass_form.is_valid():
                password = change_pass_form.cleaned_data.get("password")
                new_password = change_pass_form.cleaned_data.get("new_password")
                repeat_new_pass = change_pass_form.cleaned_data.get("repeat_new_pass")
                if password == user.password and password and new_password and repeat_new_pass:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Ваш пароль успешно изменён!")
                    return redirect('users:user_data')
    context = {'edit_contact_data_form': edit_contact_data_form,
               'change_pass_form': change_pass_form,
               "adaptive_navigation": "Контактные данные"
               }
    return render(request, 'profile_data.html', context)


@login_required
@permission_required("advertisement.add_store", raise_exception=True)
def add_store(request):
    if request.method == 'POST':
        new_store = StoreForm(request.POST, request.FILES)
        if new_store.is_valid():
            store = new_store.save(commit=False)
            store.user = request.user
            store.save()
            messages.success(request, f"Новый магазин {store} успешно создан!")
            return redirect('users:my_store')

        store_form = StoreForm(request.POST, request.FILES)
        store_form.errors.update(new_store.errors)
        context = {
            "store_form": store_form
        }
        return render(request, 'profile_add_store.html', context)

    store_form = StoreForm(initial={'contact_name': request.user.first_name, 'email': request.user.email,
                                    'phone_num': request.user.phone_number})

    context = {
        "store_form": store_form,
        "adaptive_navigation": "Добавить магазин"
    }

    return render(request, 'profile_add_store.html', context)


@login_required
@permission_required("advertisement.view_store", raise_exception=True)
def get_my_store(request):
    stores = Store.objects.filter(user=request.user).order_by('id')
    if stores.exists():
        context = {
            'stores': stores,
            "adaptive_navigation": "Мои магазины"
        }
    else:
        context = {
            "adaptive_navigation": "Мои магазины"
        }
    return render(request, 'profile_shop.html', context)


@login_required
@permission_required("advertisement.change_store", raise_exception=True)
def edit_store(request, store_id):
    store = get_object_or_404(Store, user=request.user, id=store_id)
    if request.method == 'POST':
        edit_selected_store = StoreForm(request.POST, request.FILES, instance=store)
        if edit_selected_store.is_valid():
            edit_selected_store.save()
            messages.success(request, f"Магазин {store} успешно изменён!")
            return redirect('users:my_store')
    else:
        edit_selected_store = StoreForm(instance=store)

    context = {
        'store_form': edit_selected_store,
        'selected_region': Region.objects.get(id=store.region_id),
        "adaptive_navigation": "Редактирование магазина"
    }
    return render(request, 'profile_edit_shop.html', context)


@login_required
@permission_required("advertisement.delete_store", raise_exception=True)
def delete_store(request, store_id):
    store = get_object_or_404(Store, user=request.user, id=store_id)
    if request.method == "POST":
        store.delete()
        messages.success(request, f"Магазин {store} успешно удален!")
        return redirect('users:my_store')
    context = {
        'store': store,
        "adaptive_navigation": "Удаление магазина"
    }
    return render(request, 'delete_store.html', context)


@login_required
def get_all_dialogs(request):
    """ Показывает все диалоги пользователя в ЛК """
    chats = Chat.objects.filter(members__in=[request.user.id]
                                ).annotate(last_message=Max('message__pub_date')).order_by("-last_message"
                                           ).prefetch_related('message_set', 'message_set__chat'
                                                              ).select_related('advertisement__category',
                                                                               'advertisement', 'store',
                                                                               'store__category')
    unread_chat = Message.objects.filter(chat__in=chats, is_read=False).exclude(author=request.user).exists()
    context = {
        "user_profile": request.user,
        "chats": chats,
        "unread_chat": unread_chat,
        "adaptive_navigation": "Мои сообщения"
    }
    return render(request, 'profile_dialogs.html', context)


@login_required
def view_message(request, chat_id, chat_name):
    '''Показывает все сообщения внутри открытого диалога'''
    chat = get_object_or_404(Chat, id=chat_id, members=request.user)
    Message.objects.filter(chat=chat, is_read=False).exclude(author=request.user).update(is_read=True)
    context = {
        "chat": chat,
    }
    return render(request, 'profile_dialog.html', context)


@login_required
def delete_dialogs(request):
    """ Удаление выбранного диалога в ЛК """
    if request.method == "POST":
        if 'dialog' in request.POST:
            dialog = get_object_or_404(Chat, id=request.POST.get('dialog'), members=request.user)
            dialog.members.remove(request.user)
            messages.success(request, "Диалог удален!")
        return redirect('users:dialogs')


def delete_user_message(request, message_id, chat_id):
    """ Удаление сообщения пользователя в открытом диалоге """
    if request.method == "POST":
        if 'delete_message' in request.POST:
            message = get_object_or_404(Message, id=message_id)
            message.delete()
            messages.success(request, "Сообщение удалено!")

    context = {'chat_id': chat_id}
    return redirect(reverse('users:messages', kwargs=context))


@login_required
def get_user_all_publications(request):
    """ Вывод всех публикаций """
    user_publications = Publication.objects.filter(user=request.user.id).order_by('-date_of_create')
    context = {
        "user_publications": user_publications,
        "adaptive_navigation": "Мои публикации"
    }
    return render(request=request, template_name='profile_publications.html', context=context)


@login_required
def add_user_publication(request):
    """ Добавление новой публикации """
    form_publication = PublicationForm()
    if request.method == 'POST':
        form_publication = PublicationForm(request.POST, request.FILES)
        if form_publication.is_valid():
            publication = form_publication.save(commit=False)
            publication.user = request.user
            publication.save()
            return redirect('users:user_all_publications')
    context = {
        "form_publication": form_publication,
        "adaptive_navigation": "Добавление публикации"
    }
    return render(request=request, template_name='profile_add_publication.html', context=context)


@login_required
def delete_publication(request):
    """ Удаляет выбранные публикации """
    if request.method == "POST":
        if 'delete_publication' in request.POST:
            selected_publications = request.POST.getlist('publication_checkbox')
            Publication.objects.filter(user=request.user, id__in=selected_publications).delete()
            messages.success(request, "Выбранные публикации удалены!")
            return redirect('users:user_all_publications')


@login_required
def edit_publication(request, publication_slug):
    """ Публикация для редактирования """
    publication = get_object_or_404(Publication, user=request.user, slug=publication_slug)

    if request.method == 'POST':
        form_publication = PublicationForm(request.POST, request.FILES, instance=publication)
        if form_publication.is_valid():
            publication = form_publication.save(commit=False)
            publication.moderated = False
            publication.save()
            messages.success(request, f"""Публикация "{publication}" успешно изменена
                                                    и отправлена на модерацию.""")
            return redirect('users:user_all_publications')
    else:
        form_publication = PublicationForm(instance=publication)

    context = {
        'publication': publication,
        'form_publication': form_publication,
        "adaptive_navigation": "Редактирование публикации"
    }
    return render(request=request, template_name='profile_edit_publication.html', context=context)


@login_required
def get_favorites_page(request):
    favorites_list = Advertisement.objects.filter(id__in=request.user.userfavorites.favorites, is_active=True,
                                                  moderated=True)
    context = {
        "favorites_list": favorites_list,
        "adaptive_navigation": "Избранное"
    }
    return render(request, "profile_favorites.html", context)
