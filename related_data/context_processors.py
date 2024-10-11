from django.core.cache import cache

from .models import Category, Region


def get_data_category_and_region(request):
    """
    Добавляет данные моделей Category и Region в контекст шаблона,
    и при необходимости кэширует эти данные
    """
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
