import os

from pydantic import SecretStr, BaseSettings


class GlobalConfigs(BaseSettings):
    telegram_token_bot = SecretStr(os.getenv("TELEGRAM_BOT_TOKEN"))
    redis_host = str(os.getenv("REDIS_HOST", "localhost"))
    redis_password = SecretStr(os.getenv("REDIS_AUTH", ""))
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DATABASE", 0))
