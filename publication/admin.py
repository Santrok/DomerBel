from django.contrib import admin

from .models import Publication, PublicationAdmin

# Register your models here.
admin.site.register(Publication, PublicationAdmin)
