import os

from pydantic import SecretStr, BaseSettings


class GlobalConfigs(BaseSettings):
    default_inactive_message = """Hello!
It's been a while since I've seen you(
I miss you."""
    pre_prompt = """"""
    inactive_days = int(os.getenv("INACTIVE_DAYS", 7))
    telegram_token_bot = SecretStr(os.getenv("TELEGRAM_BOT_TOKEN"))
    redis_host = str(os.getenv("REDIS_HOST", "localhost"))
    redis_password = SecretStr(os.getenv("REDIS_AUTH", ""))
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DATABASE", 0))
    inactive_message = str(os.getenv("INACTIVE_MESSAGE", default_inactive_message))
