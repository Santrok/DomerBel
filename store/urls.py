from django.urls import path

from .views import (get_stores_page, get_store_search_page, get_store_by_title, get_store_by_title_and_category,
                    get_page_search_result_for_advertisements_in_the_store, get_stores_by_category,
                    get_page_for_add_new_store, get_page_for_edit_store, get_page_for_delete_store,
                    activate_or_deactivate_selected_store)

urlpatterns = [
    path('', get_stores_page, name='stores'),
    path('search_results/', get_store_search_page, name='stores_search_results'),
    path('add_store/', get_page_for_add_new_store, name='add_store'),
    path('store_edit/<int:store_id>/', get_page_for_edit_store, name='edit_store'),
    path('change_store_status/', activate_or_deactivate_selected_store, name='change_store_status'),
    path('delete_store/<int:store_id>/', get_page_for_delete_store, name='delete_store'),
    path('store/<slug:store_slug>/', get_store_by_title, name='store_by_title'),
    path('<slug:category_slug>/', get_stores_by_category, name='stores_by_category'),
    path('store/<slug:store_slug>/search/', get_page_search_result_for_advertisements_in_the_store,
         name='search_for_advertisements_in_the_store'),
    path('store/<slug:store_slug>/<slug:category_slug>/', get_store_by_title_and_category,
         name='store_by_title_and_category'),
]
