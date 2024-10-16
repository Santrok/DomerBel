from django.contrib import admin

from .models import Store, StoreAdmin

# Register your models here.
admin.site.register(Store, StoreAdmin)
