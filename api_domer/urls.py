from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


from api_domer.views import get_list_of_cities, get_list_of_categories, get_region_list, get_category_list, \
    get_categories_for_search, get_field_list, get_elementtwo_list, save_advertisement, get_store_for_advertisement, \
    update_advertisement, registration_user, login_user, logout_user, password_reset, add_to_favorite, \
    get_subcategory_list, \
    get_element_list, delete_from_favorite, ReasonOfComplaintView, save_complaint, create_chat, get_bulk_import_of_ads, \
    status_unread_message_user

urlpatterns = [
    path('get_city_list/<int:id>', get_list_of_cities, name='list_of_cities'),
    path('add_store/categories/', get_list_of_categories, name='list_of_categories'),
    path('categories_for_search/<int:id>', get_categories_for_search, name='categories_for_search'),
    path('get_region_list/', get_region_list),
    path('get_category_list/', get_category_list),
    path('get_field_list/', get_field_list),
    path('get_elementtwo_list/', get_elementtwo_list),
    path('save_advertisement/', save_advertisement, name='save_advertisement'),
    path('get_store_for_advertisement/', get_store_for_advertisement, name='get_store_for_advertisement'),
    path('update_advertisement/', update_advertisement),
    path('registration_user/', registration_user),
    path('login_user/', login_user),
    path('logout/', logout_user),
    path('password_reset/', password_reset),
    path('add_to_favorite/', add_to_favorite),
    path('delete_from_favorite/', delete_from_favorite),
    path('get_element_list/', get_element_list),
    path('get_subcategory_list/', get_subcategory_list),
    path('get_complaint_reason_list/', ReasonOfComplaintView.as_view()),
    path('save_complaint/', save_complaint),
    path('create_chat/', create_chat),
    path('get_bulk_import_of_ads/', get_bulk_import_of_ads),
    path('status_unread_message_user/', status_unread_message_user),

]
