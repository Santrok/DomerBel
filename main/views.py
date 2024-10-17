from django.contrib import messages
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect

from advertisement.models import Advertisement
from config import settings
from main.forms import FeedbackForm
from main.models import Help
from related_data.models import Category
from services.email.message import run_send_email_task_celery


# Create your views here.

def get_main_page(request):
    """
    Сборка главной базовой страницы с последними поданными объявлениями.
    Модели: Advertisement
    """

    advertisement_queryset = Advertisement.objects.filter(is_active=True,
                                                          moderated=True).select_related(
        'category', 'region').order_by("-search_boost_date")[:10].defer(
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
    vip_advertisement = Advertisement.objects.filter(vip=True,
                                                     shown_vip=True,
                                                     is_active=True,
                                                     moderated=True)
    context = {
        "advertisement": advertisement_queryset,
        "vip_advertisement": vip_advertisement,
        "adaptive_navigation": "Общебелорусская доска объявлений"
    }
    return render(request, 'main.html', context)


def get_site_map_page(request):
    """
    Сборка страницы "Карта сайта".
    Модели: Category
    """

    category_list = Category.objects.prefetch_related('field_set__spisok__element_set',
                                                      'field_set')

    context = {
        'nodes': category_list,
        "adaptive_navigation": "Карта сайта"
    }
    per = Permission.objects.get(codename='add_store')
    print(per)
    return render(request, 'map.html', context)


def get_feedback_page_and_send_feedback_to_administration_email(request):
    """
    Сборка страницы "Обратная связь".
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
    """
    Сборка страницы помощь.
    Модель: Help
    """

    context = {
        "help": Help.objects.first(),
    }
    return render(request, "help_page.html", context)


def get_page_not_found(request):
    """
    Возвращает кастомную страницу ошибки 404
    """
    return render(request, '404.html', status=404)
