from django.apps import AppConfig


class RelatedDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'related_data'

    def ready(self):
        import related_data.signals
