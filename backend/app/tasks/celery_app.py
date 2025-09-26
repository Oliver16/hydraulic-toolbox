from __future__ import annotations

import os

from celery import Celery

from ..db import settings

celery_app = Celery(
    "hydraulic",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=bool(int(os.getenv("CELERY_ALWAYS_EAGER", "0"))),
)

