from django.contrib import admin

from .models import (Help, AboutOrganization, BadWords, HelpAdmin, AboutOrganizationAdmin, BadWordsAdmin,
                     PaidInformation, PaidInformationAdmin)

# Register your models here.
admin.site.register(Help, HelpAdmin)
admin.site.register(AboutOrganization, AboutOrganizationAdmin)
admin.site.register(BadWords, BadWordsAdmin)
admin.site.register(PaidInformation, PaidInformationAdmin)

admin.site.site_header = "Администрирование сайта ДОМЕР.бел"
admin.site.site_title = "Администрирование сайта"
admin.site.index_title = "Администрирование сайта"
