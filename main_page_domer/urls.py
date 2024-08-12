from django.urls import path

from main_page_domer.views import *


urlpatterns = [
    path('', get_main_page, name='home'),
    path('stores/', get_stores_page, name='stores'),
    path('stores/search_results/', get_store_search, name='stores_search_results'),
    path('stores/<slug:category_slug>/', get_stores_by_category, name='stores_by_category'),
    path('store/<slug:store_slug>/', get_store_by_title, name='store_by_title'),
    path('store/<slug:store_slug>/<slug:category_slug>/', get_store_by_title_and_category, name='store_by_title_and_category'),
    path('stores/<slug:store_slug>/search/', search_for_advertisements_in_the_store, name='search_for_advertisements_in_the_store'),
    path('help/', get_help_page, name='help'),
    path('site_map/', get_site_map_page, name='site_map'),
    path("publications/", get_publications, name="publications"),
    path("publication/<str:slug>", get_publication_by_slug, name="publication_by_slug"),
    path("publication/search/", publication_search_result, name="publication_search_result"),
    path('feedback/', get_feedback_page, name='feedback'),
    path('complaint_about_adv_id_<int:adv_id>/', get_complaint_page, name='complaint'),
    path('register_done', register_done, name='register_done'),
    path('download/', download_advertis),
    path('download_user/', dowload_user),
    path('download_photo/', dowload_photo),
]
