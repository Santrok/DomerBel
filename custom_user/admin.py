from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserFavorites, UserFavoritesAdmin


# Register your models here.


class CustomUserAdmin(UserAdmin):
    """Класс управления отображения в админ панели сущности: User"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()
    list_display = ("email", "is_active", "entity")
    list_filter = ("is_active", "entity")
    list_editable = ("is_active", "entity")
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "phone_number", "entity")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
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
    ordering = ("-date_joined",)


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(UserFavorites, UserFavoritesAdmin)
