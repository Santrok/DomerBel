from django.apps import AppConfig


class RelatedDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'related_data'
    verbose_name = 'Вспомогательная информация'

    def ready(self):
        import related_data.signals
