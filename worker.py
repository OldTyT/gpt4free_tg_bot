import os
import sys

from rq import Connection, Worker
from redis import Redis
from pydantic import SecretStr

from logger import logger


def start_rq_worker():
    try:
        redis_conn = Redis(
            host = str(os.getenv("REDIS_HOST", "localhost")),
            password = SecretStr(os.getenv("REDIS_AUTH", "")),
            port = int(os.getenv("REDIS_PORT", 6379)),
            db = int(os.getenv("REDIS_DATABASE", 0))
        )
        with Connection(connection=redis_conn):
            qs = sys.argv[1:] or 'fast_gpt4_bot_queue'
            Worker(qs).work(burst=True)
    except Exception as e:
        logger.error("Fatal error: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    start_rq_worker()
