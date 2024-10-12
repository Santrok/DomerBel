from django.contrib import admin

from .models import Service, ServiceAdmin

# Register your models here.
admin.site.register(Service, ServiceAdmin)
