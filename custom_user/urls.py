from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy

from .views import get_user_data_page_and_change_user_data

urlpatterns = [
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html",
                                          success_url=reverse_lazy("password_reset_complete")),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('user_data/', get_user_data_page_and_change_user_data, name='user_data'),
]
