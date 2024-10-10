from django.contrib import admin

from .models import Chat, UserMessage

# Register your models here.
admin.site.register(Chat)
admin.site.register(UserMessage)
