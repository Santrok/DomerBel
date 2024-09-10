import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

'''плановые задачи'''
app.conf.beat_schedule = {
    "deactivate_advertisement": {
        "task": 'advertisement.tasks.deactivate_advertisement',
        "schedule": timedelta(seconds=10)
        # "schedule": crontab(hour=0, minute=1)
    },
    "delete_advertisement": {
        "task": 'advertisement.tasks.delete_advertisement',
        "schedule": timedelta(seconds=10)
        # "schedule": crontab(hour=0, minute=1)
    },
    "deactivate_store": {
        "task": 'advertisement.tasks.deactivate_store',
        "schedule": timedelta(seconds=10)
        # "schedule": crontab(hour=0, minute=1)
    },
    "delete_everything_in_folder": {
        "task": "advertisement.tasks.delete_everything_in_folder_beat",
        "schedule": crontab(minute=15, hour=0),
    },
    "delete_error_file": {
        "task": "advertisement.tasks.delete_error_file_beat",
        # "schedule": crontab(minute=15, hour=0),
        "schedule": timedelta(seconds=120)
    }
}

if __name__ == '__main__':
    app.start()
