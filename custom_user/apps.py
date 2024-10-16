from django.apps import AppConfig


class CustomUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_user'
    verbose_name = "Пользователи"

    def ready(self):
        import custom_user.signals
