from django.contrib import admin

from .models import Help, AboutOrganization, BadWords

# Register your models here.
admin.site.register(Help)
admin.site.register(AboutOrganization)
admin.site.register(BadWords)
