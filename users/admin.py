from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import MyCustomUserCreationForm, CustomUserChangeForm
from .models import User, Chat, Message, UserFavorites


class CustomUserAdmin(UserAdmin):
    add_form = MyCustomUserCreationForm
    form = CustomUserChangeForm
    model = User
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


admin.site.register(User, CustomUserAdmin)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(UserFavorites)