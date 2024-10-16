from django.contrib import admin

from .models import (Region, Category, Field, Spisok, Element, ElementTwo, RegionAdmin, CategoryAdmin, FieldAdmin,
                     SpisokAdmin, ElementAdmin, ElementTwoAdmin)

# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Spisok, SpisokAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(ElementTwo, ElementTwoAdmin)
