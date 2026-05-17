from celery import Celery
from app.config import settings

celery_app = Celery("stock_screener", broker=settings.REDIS_URL)
celery_app.config_from_object("app.tasks.schedules")
