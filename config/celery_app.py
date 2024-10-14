import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Время жизни ключей результатов задач в Redis в секундах.
app.conf.result_expires = 15

"""плановые задачи"""
app.conf.beat_schedule = {
    "deactivate_advertisement": {
        "task": 'advertisement.tasks.deactivate_advertisement',
        # "schedule": timedelta(seconds=10)
        "schedule": crontab(hour=0, minute=1)
    },
    "delete_advertisement": {
        "task": 'advertisement.tasks.delete_advertisement',
        # "schedule": timedelta(seconds=10)
        "schedule": crontab(hour=0, minute=1)
    },
    "deactivate_store": {
        "task": 'advertisement.tasks.deactivate_store',
        # "schedule": timedelta(seconds=10)
        "schedule": crontab(hour=0, minute=1)
    },
    "delete_everything_in_folder": {
        "task": "advertisement.tasks.delete_everything_in_folder_beat",
        "schedule": crontab(minute=15, hour=0),
    },
    "delete_error_file": {
        "task": "advertisement.tasks.delete_error_file_beat",
        "schedule": crontab(minute=15, hour=0),
        # "schedule": timedelta(seconds=120)
    },
    "list_shown_vip": {
        "task": "advertisement.tasks.list_shown_vip",
        "schedule": timedelta(seconds=60)
    },
    "list_shown_vip_category": {
        "task": "advertisement.tasks.list_shown_vip_category",
        "schedule": timedelta(seconds=60)
    },
    "update_schedule": {
        "task": "advertisement.tasks.update_schedule",
        # "schedule": timedelta(seconds=15)
        "schedule": crontab(hour=0, minute=1)
    }
}

if __name__ == '__main__':
    app.start()
