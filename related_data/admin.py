from django.contrib import admin

from .models import Region, Category, Field, Spisok, Element, ElementTwo

# Register your models here.
admin.site.register(Region)
admin.site.register(Category)
admin.site.register(Field)
admin.site.register(Spisok)
admin.site.register(Element)
admin.site.register(ElementTwo)
