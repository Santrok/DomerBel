from django.contrib import admin
from main_page_domer.models import (Complaint, ReasonOfComplaint, Publication, PublicationAdmin, Comment,
                                    PhotoPublication, Help, AboutOrganization)


class PublicationAdmin(admin.ModelAdmin):
    """ Модель публикации для Админки """
    list_display = ("id",
                    "title",
                    "slug",
                    'moderated',
                    )
    list_display_links = ["title", ]
    search_fields = ('title',)
    list_filter = ('moderated',)
    prepopulated_fields = {"slug": ("title",)}
    ordering = ["date_of_create", ]
    list_editable = ["moderated", ]  # Потом УДАЛИТЬ! редактируем поле "прошел модерацию" не заходя в публикацию


admin.site.register(Complaint)
admin.site.register(ReasonOfComplaint)
admin.site.register(PhotoPublication)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Comment)
admin.site.register(Help)
