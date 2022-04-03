from celery.schedules import crontab
from celery import current_app as current_celery_app

from project.config import settings


def create_celery():
    # Rather than creating a new Celery instance, we used current_app so that shared tasks will work as expected
    celery_app = current_celery_app

    # means all celery-related configuration keys should be prefixed with CELERY_.
    # For example, to configure the broker_url, we should use CELERY_BROKER_URL
    celery_app.config_from_object(settings, namespace="CELERY")

    # disable UTC so that Celery can use local time
    celery_app.conf.enable_utc = False

    # add "crawl_url" task to the beat schedule
    celery_app.conf.beat_schedule = {
        "crawl_url": {
            "task": "project.news.tasks.crawl_url",
            "schedule": crontab(minute="*/1"),
        }
    }
    return celery_app