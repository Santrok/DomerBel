from django.urls import path

from .views import get_advertisement_page, get_advertisement_by_category, get_page_place_an_ad, \
    get_advertisement_details_page, get_page_place_an_favorites, editing_an_ad, search_result, \
    get_page_place_an_favorites, get_bulk_import_of_ads
from .views import get_advertisement_page, get_advertisement_by_category, get_page_place_an_ad, \
    get_advertisement_details_page, get_page_place_an_favorites, editing_an_ad, get_instructions_for_bulk_import_of_ads

urlpatterns = [
    path('', get_advertisement_page, name='advertisement'),
    path('advertisement/<slug:category_slug>/', get_advertisement_by_category, name='advertisement_by_category'),
    path('place_an_ad/', get_page_place_an_ad, name='place_an_ad'),
    path('favorites/', get_page_place_an_favorites, name='favorites'),
    path('advertisement_details/<slug:slug>/', get_advertisement_details_page, name='advertisement_details'),
    path('import_bulk_of_ads/',get_bulk_import_of_ads),
    path('advertisement_details/<int:id>/', get_advertisement_details_page, name='advertisement_details'),
    path('instructions_for_bulk_import_of_ads', get_instructions_for_bulk_import_of_ads, name='instructions'),
    path('advertisement_details/<str:slug>/', get_advertisement_details_page, name='advertisement_details'),
    path('editing_an_ad/<int:id>/', editing_an_ad, name='editing_an_ad'),
    path('search_result/', search_result, name='search_result'),
    # path('import_words', import_words),
]
