from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from config import settings
from publication.forms import PublicationForm
from publication.models import Publication
from services.email.message import run_send_email_task_celery
from utils.template_paginator import variables_for_paginator


# Create your views here.


def get_publications_page(request):
    """
    Сборка страницы со всеми публикациями.
    Модели: Publication
    """
    publications = Publication.objects.exclude(moderated=False).order_by('-date_of_create')

    page_obj = variables_for_paginator(publications,
                                       request.GET.get('page'),
                                       10)

    context = {
        'publications_count': publications.count(),
        'publications': page_obj,
        'adaptive_navigation': 'Публикации. Беларусь'
    }
    return render(request, 'publications.html', context)


def get_publication_page_by_slug(request, slug):
    """
    Сборка страницы с детальной информацией выбранной публикации.
    Модели: Publication
    """
    Publication.objects.filter(slug=slug).update(counter_views=F('counter_views')+1)
    publication = get_object_or_404(Publication, slug=slug, moderated=True)
    context = {
        'publication': publication,
        'adaptive_navigation': f'{publication.title}'
    }
    return render(request, 'publication_by_slug.html', context)


def get_search_result_page_by_publication(request):
    """
    Сборка страницы с результатами поиска по публикациям.
    Модели: Publication
    """
    search_parameters = {}

    if request.GET.get('only_title') and request.GET.get('text_search'):
        search_parameters['search_title_vector'] = request.GET.get('text_search')
    elif request.GET.get('text_search'):
        search_parameters['search_vector'] = request.GET.get('text_search')

    query = request.META.get('QUERY_STRING').replace(f'page={request.GET.get("page")}&', '')

    publications = Publication.objects.filter(moderated=True,
                                              **search_parameters
                                              ).order_by('-date_of_create')

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


@login_required
def get_page_for_add_new_publication(request):
    """
    Сборка страницы с для создания новой публикации.
    Отправка уведомления о создании публикации администрации сайта.
    Модели: Publication
    """
    form_publication = PublicationForm()
    if request.method == 'POST':
        form_publication = PublicationForm(request.POST, request.FILES)
        if form_publication.is_valid():
            publication = form_publication.save(commit=False)
            publication.user = request.user
            publication.save()
            messages.success(request, """Ваша публикация отправлен на модерацию.
                                         После модерации она появится в списке публикаций.""")
            run_send_email_task_celery('Добавлена новая публикация',
                                       'asend_notification.html',
                                       settings.EMAIL_HOST_USER,
                                       subject="Добавлена публикация",
                                       message=f'Новая публикация требует модерации на сайте Домер.бел',
                                       link=f"/admin/publication/publication/{publication.id}/change/",
                                       )
            return redirect('user_all_publications')
    context = {
        "form_publication": form_publication,
        "adaptive_navigation": "Добавление публикации"
    }
    return render(request=request, template_name='profile_add_publication.html', context=context)


@login_required
def delete_publication(request):
    """
    Функция для удаления выбранных публикаций пользователя.
    Модели: Publication
    """
    if request.method == "POST":
        if 'delete_publication' in request.POST:
            selected_publications = request.POST.getlist('publication_checkbox')
            Publication.objects.filter(user=request.user, id__in=selected_publications).delete()
            messages.success(request, "Выбранные публикации удалены!")
            return redirect('user_all_publications')


@login_required
def get_page_for_edit_publication(request, publication_slug):
    """
    Сборка страницы редактирования выбранной публикации пользователя.
    Отправка уведомления о редактировании публикации администрации сайта.
    Модели: Publication
    """
    publication = get_object_or_404(Publication, user=request.user, slug=publication_slug)

    if request.method == 'POST':
        form_publication = PublicationForm(request.POST, request.FILES, instance=publication)
        if form_publication.is_valid():
            publication = form_publication.save(commit=False)
            publication.moderated = None
            publication.save()
            messages.success(request, """Ваша публикация отправлена на модерацию.
                                         После модерации она появится в списке публикаций.""")
            run_send_email_task_celery('Изменена публикация',
                                       'asend_notification.html',
                                       settings.EMAIL_HOST_USER,
                                       subject="Изменена публикация",
                                       message=f'Публикация {publication.id} требует модерации на сайте Домер.бел',
                                       link=f"/admin/publication/publication/{publication.id}/change/"
                                       )
            return redirect('user_all_publications')
    else:
        form_publication = PublicationForm(instance=publication)

    context = {
        'publication': publication,
        'form_publication': form_publication,
        "adaptive_navigation": "Редактирование публикации"
    }
    return render(request=request, template_name='profile_edit_publication.html', context=context)
