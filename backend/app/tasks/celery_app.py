from celery import Celery
from celery.signals import worker_process_init
from app.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "stock_screener",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
)
celery_app.config_from_object("app.tasks.schedules")
celery_app.autodiscover_tasks(["app.tasks.data_fetch", "app.tasks.screening_run"])


@worker_process_init.connect
def init_criteria_registry(**kwargs):
    from app.core.screening.registry import CriteriaRegistry
    CriteriaRegistry.discover()
