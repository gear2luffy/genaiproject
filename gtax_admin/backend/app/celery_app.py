"""
Celery configuration for background tasks.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_trading",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.scanner_tasks",
        "app.tasks.signal_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.scanner_tasks.*": {"queue": "scanner"},
        "app.tasks.signal_tasks.*": {"queue": "signals"},
    },
    beat_schedule={
        "scan-markets-every-minute": {
            "task": "app.tasks.scanner_tasks.scan_markets",
            "schedule": 60.0,
        },
        "update-positions-every-5-minutes": {
            "task": "app.tasks.signal_tasks.update_positions",
            "schedule": 300.0,
        },
    }
)
