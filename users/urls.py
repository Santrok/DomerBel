from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy


from .views import (get_favorites_page, get_personal_account_page,add_store, get_my_store,
                    edit_store, delete_store, get_user_data_page,
                    get_personal_account_inactive_adds_page, delete_or_archive_selected_ads,
                    search_of_ads_in_personal_account, get_user_all_publications, add_user_publication,
                    delete_publication, edit_publication, get_all_dialogs, view_message,
                    delete_dialogs, delete_user_message)

app_name = 'users'

urlpatterns = [
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html",
                                          success_url=reverse_lazy("users:password_reset_complete")),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('personal_account/', get_personal_account_page, name='personal_account'),
    path('personal_account/search_results', search_of_ads_in_personal_account, name="personal_account_search_results"),
    path('personal_account/delete_or_archive_ads/', delete_or_archive_selected_ads, name='delete_or_archive_ads'),
    path('personal_account/archived_adds/', get_personal_account_inactive_adds_page, name='inactive_adds'),
    path('user_data/', get_user_data_page, name='user_data'),
    path('add_store/', add_store, name='add_store'),
    path('my_store/', get_my_store, name='my_store'),
    path('edit_store/<int:store_id>/', edit_store, name='edit_store'),
    path('delete_store/<int:store_id>/', delete_store, name='delete_store'),
    path('dialogs/', get_all_dialogs, name='dialogs'),
    path('dialogs/<str:chat_name>/<int:chat_id>/', view_message, name='messages'),
    path('dialogs/delete_dialogs/', delete_dialogs, name="delete_dialogs"),
    path('dialogs/<int:chat_id>/delete_user_message/<int:message_id>/', delete_user_message, name="delete_user_message"),
    path('personal_account/my_publications/', get_user_all_publications, name='user_all_publications'),
    path('add_publication/', add_user_publication, name='add_publication'),
    path('personal_account/delete_publication/', delete_publication, name='delete_publication'),
    path('personal_account/edit_publication/<str:publication_slug>/', edit_publication, name='edit_publication'),
    path('personal_account/favorites/', get_favorites_page, name='favorites'),
]
