from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_user'
    verbose_name = _("Authentication and Authorization")

    def ready(self):
        import custom_user.signals
