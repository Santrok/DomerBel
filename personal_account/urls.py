from django.urls import path

from personal_account.views import (get_page_in_personal_account_with_active_advertisements,
                                    get_page_in_personal_account_with_inactive_advertisements,
                                    get_page_in_personal_account_with_search_result_by_user_advertisement,
                                    delete_or_archive_selected_ads, get_page_in_personal_account_with_user_stores,
                                    get_user_favorites_page, get_page_in_personal_account_all_user_publications)

urlpatterns = [
    path('', get_page_in_personal_account_with_active_advertisements, name='personal_account'),
    path('archived_adds/', get_page_in_personal_account_with_inactive_advertisements, name='inactive_adds'),
    path('search_results_by_advertisement/',
         get_page_in_personal_account_with_search_result_by_user_advertisement,
         name="personal_account_search_results"),
    path('delete_or_archive_ads/', delete_or_archive_selected_ads, name='delete_or_archive_ads'),
    path('my_stores/', get_page_in_personal_account_with_user_stores, name='my_store'),
    path('my_publications/', get_page_in_personal_account_all_user_publications, name='user_all_publications'),
    path('favorites/', get_user_favorites_page, name='favorites'),
]