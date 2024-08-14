from django.core.cache import cache

from main_page_domer.models import AboutOrganization


def get_data_about_organization(request):
    about_organization = cache.get('about_organization')

    if about_organization is None:
        about_organization = AboutOrganization.objects.first()
        cache.set('about_organization', about_organization)

    context = {
        "about_organization": about_organization,
    }
    return context
