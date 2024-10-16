from django.urls import path

from chat.views import get_all_user_dialogs, view_message_in_dialog, delete_user_dialog

urlpatterns = [
    path('dialogs/', get_all_user_dialogs, name='dialogs'),
    path('dialogs/<str:chat_name>/<int:chat_id>/', view_message_in_dialog, name='messages'),
    path('delete_dialogs/', delete_user_dialog, name="delete_dialogs"),
]
