from django.urls import path

from .views import (save_advertisement, update_advertisement, registration_user, login_user, logout_user,
                    password_reset, save_complaint_and_send_complaint_to_administration_email,
                    create_new_chat_and_create_new_message, status_unread_message_user, add_to_favorite,
                    delete_from_favorite, providing_a_payment_page, processing_successful_payment_for_services,
                    get_region_list, get_category_list, get_subcategory_list, get_field_list, get_elementtwo_list,
                    get_store_list_by_user, get_list_of_cities, get_element_list, get_result_task,
                    get_bulk_import_of_ads, add_new_notes_for_favorites)

urlpatterns = [
    path('save_advertisement/', save_advertisement),
    path('update_advertisement/', update_advertisement),
    path('save_complaint/', save_complaint_and_send_complaint_to_administration_email),
    path('create_chat/', create_new_chat_and_create_new_message),
    path('status_unread_message_user/', status_unread_message_user),
    path('registration_user/', registration_user),
    path('login_user/', login_user),
    path('logout/', logout_user),
    path('password_reset/', password_reset),
    path('add_to_favorite/', add_to_favorite),
    path('delete_from_favorite/', delete_from_favorite),
    path('send_paid/', providing_a_payment_page),
    path('notification/', processing_successful_payment_for_services),
    path('get_region_list/', get_region_list),
    path('get_city_list/<int:id>', get_list_of_cities),
    path('get_category_list/', get_category_list),
    path('get_subcategory_list/', get_subcategory_list),
    path('get_field_list/', get_field_list),
    path('get_element_list/', get_element_list),
    path('get_elementtwo_list/', get_elementtwo_list),
    path('get_store_for_advertisement/', get_store_list_by_user),
    path('get_bulk_import_of_ads/', get_bulk_import_of_ads),
    path('get_result_task/<str:id>', get_result_task),
    path('add_new_notes_for_favorites/', add_new_notes_for_favorites)
]
