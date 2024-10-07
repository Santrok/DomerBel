from datetime import date, timedelta
from functools import cached_property

from django.core.cache import cache

from advertisement.models import Category, Region
from main_page_domer.models import AboutOrganization


def get_date_today(request):
    date_today = date.today()
    date_yesterday = date_today - timedelta(1)

    context = {
        "date_today": date_today,
        "date_yesterday": date_yesterday,

    }
    return context



def get_data_category_and_region(request):
    category = cache.get('category')
    region = cache.get('region')

    if category is None:
        category = Category.objects.filter(level__lte=1)
        cache.set('category', category)

    if region is None:
        region = Region.objects.all()
        cache.set('region', region)

    context = {
        "category_list": category,
        "region_list": region
    }
    return context
