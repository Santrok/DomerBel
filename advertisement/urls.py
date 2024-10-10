from django.urls import path

from .views import (get_advertisement_page, get_advertisement_by_category, get_page_place_an_advertisement,
                    get_advertisement_details_page, get_page_editing_an_advertisement,
                    get_page_search_result_by_advertisements, get_page_for_bulk_import_of_advertisement,
                    get_page_for_instructions_for_bulk_import_of_ads,)

urlpatterns = [
    path('', get_advertisement_page, name='advertisement'),
    path('search_result/', get_page_search_result_by_advertisements, name='search_result'),
    path('advertisement/<slug:category_slug>/', get_advertisement_by_category, name='advertisement_by_category'),
    path('place_an_ad/', get_page_place_an_advertisement, name='place_an_ad'),
    path('editing_an_ad/<int:id>/', get_page_editing_an_advertisement, name='editing_an_ad'),
    path('advertisement_details/<slug:slug>/', get_advertisement_details_page, name='advertisement_details'),
    path('instructions_for_bulk_import_of_ads', get_page_for_instructions_for_bulk_import_of_ads, name='instructions'),
    path('advertisement_details/<str:slug>/', get_advertisement_details_page, name='advertisement_details'),
    path('import_bulk_of_ads/', get_page_for_bulk_import_of_advertisement, name='bulk_import'),
]
