from django.contrib import admin

from .models import Chat, UserMessage, ChatAdmin, UserMessageAdmin

# Register your models here.
admin.site.register(Chat, ChatAdmin)
admin.site.register(UserMessage, UserMessageAdmin)
