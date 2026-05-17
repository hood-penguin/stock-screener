from celery.schedules import crontab
from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    "fetch-kr-market": {
        "task": "app.tasks.data_fetch.fetch_kr_market",
        "schedule": crontab(hour=6, minute=40),  # 06:40 UTC
    },
    "fetch-us-market": {
        "task": "app.tasks.data_fetch.fetch_us_market",
        "schedule": crontab(hour=21, minute=30),  # 21:30 UTC
    },
    "run-kr-screening": {
        "task": "app.tasks.screening_run.run_screening",
        "args": ("KR",),
        "schedule": crontab(hour=7, minute=0),  # 07:00 UTC
    },
    "run-us-screening": {
        "task": "app.tasks.screening_run.run_screening",
        "args": ("US",),
        "schedule": crontab(hour=22, minute=0),  # 22:00 UTC
    },
}

CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
