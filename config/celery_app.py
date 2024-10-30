import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

import logging
from logging import handlers
from celery.signals import setup_logging
from config.settings import BASE_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Время жизни ключей результатов задач в Redis в секундах.
app.conf.result_expires = 1800

#настройки логирования селери
@setup_logging.connect
def config_loggers(*args, **kwargs) -> None:
    logger_celery = logging.getLogger('celery')
    logger_celery.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        fmt= '{asctime} - [{levelname}] - module: {module} - [{process:d}]-[{thread:d}]: {message}',
        style='{',
    )
    handler = handlers.TimedRotatingFileHandler(
        filename = os.path.join(BASE_DIR,'logs','celery','celery.log'),
        when='midnight',
        backupCount=100,
        encoding='utf-8',
    )
    handler.setFormatter(formatter)
    logger_celery.addHandler(handler)



"""плановые задачи"""
app.conf.beat_schedule = {
    "deactivate_advertisement": {
        "task": 'advertisement.tasks.deactivate_advertisement',
        # "schedule": timedelta(seconds=10),
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
    "delete_upload_file_beat": {
        "task": "advertisement.tasks.delete_upload_file_beat",
        "schedule": crontab(minute=15, hour=0),
        # "schedule": timedelta(seconds=120)
    },
    "list_shown_vip": {
        "task": "advertisement.tasks.list_shown_vip",
        "schedule": timedelta(seconds=60),
        "options": {
            "expires": 180,
        },
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