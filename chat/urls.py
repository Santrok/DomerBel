from django.urls import path

from chat.views import chat_page

urlpatterns = [
    path("", chat_page, name="chat-page"),

]