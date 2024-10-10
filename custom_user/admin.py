from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserFavorites

# Register your models here.


class CustomUserAdmin(UserAdmin):
    """Класс управления отображения
        в админ панели сущности: User"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "phone_number", "entity")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(UserFavorites)
