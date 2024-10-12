from django.contrib import admin

from .models import Help, AboutOrganization, BadWords, HelpAdmin, AboutOrganizationAdmin, BadWordsAdmin

# Register your models here.
admin.site.register(Help, HelpAdmin)
admin.site.register(AboutOrganization, AboutOrganizationAdmin)
admin.site.register(BadWords, BadWordsAdmin)
