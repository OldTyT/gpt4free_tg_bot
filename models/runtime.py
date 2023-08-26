"""Class with runtime settings."""
from datetime import datetime

from pydantic import BaseSettings
from redis import Redis
from rq import Queue


class RuntimeSettings(BaseSettings):
    """Class with runtime settings."""

    redis_conn: Redis
    rq_queue: Queue
    started_at: datetime
    last_update: datetime
