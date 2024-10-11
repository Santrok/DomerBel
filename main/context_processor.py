from django.core.cache import cache

from .models import AboutOrganization


def get_data_about_organization(request):
    """
    Функция кеширования установочных данных об организации ДОМЕР.бел
    и передача их в контекст шаблона
    """
    about_organization = cache.get('about_organization')

    if about_organization is None:
        about_organization = AboutOrganization.objects.last()
        cache.set('about_organization', about_organization)

    context = {
        "about_organization": about_organization,
    }
    return context
