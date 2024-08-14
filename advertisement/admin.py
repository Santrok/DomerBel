from django.contrib import admin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin

from advertisement.models import Advertisement, Category, Region, PhotoAdvertisement, \
    Field, Spisok, Element, ElementTwo, Store, BadWords, UploadFile, ErrorFile


class AdvertisementAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class CategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    mptt_level_indent = 30
    max_level_indent = 3

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ограничиваем уровень вложенности каждой категории
        return qs.filter(level__lte=self.max_level_indent)


class RegionAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("area",)}
    mptt_level_indent = 30
    max_level_indent = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ограничиваем уровень вложенности каждого региона
        return qs.filter(level__lte=self.max_level_indent)


class GalleryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class StoreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(PhotoAdvertisement)
admin.site.register(Field)
admin.site.register(Spisok)
admin.site.register(Element)
admin.site.register(ElementTwo)
admin.site.register(BadWords)
admin.site.register(Store, StoreAdmin)
admin.site.register(UploadFile)
admin.site.register(ErrorFile)


