from django.urls import path

from .views import (get_main_page,
                    get_site_map_page,
                    get_feedback_page_and_send_feedback_to_administration_email,
                    get_help_page)

urlpatterns = [
    path('', get_main_page, name='home'),
    path('site_map/', get_site_map_page, name='site_map'),
    path('feedback/', get_feedback_page_and_send_feedback_to_administration_email, name='feedback'),
    path('help/', get_help_page, name='help'),
]
