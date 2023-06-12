import os
import asyncio
import logging
import logger
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from redis import Redis
from pydantic import SecretStr
from rq import Queue, Retry

from models.runtime import RuntimeSettings
from jobs import GenerateTextWithGPTModel


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)

redis_conn = Redis(
    host = str(os.getenv("REDIS_HOST", "localhost")),
    password = SecretStr(os.getenv("REDIS_AUTH", "")),
    port = int(os.getenv("REDIS_PORT", 6379)),
    db = int(os.getenv("REDIS_DATABASE", 0))
)

state_cfg = RuntimeSettings(
    redis_conn=redis_conn,
    rq_queue=Queue(os.getenv("REDIS_QUEUE", "fast_gpt4_bot_queue"), connection=redis_conn),
    started_at=datetime.now(timezone.utc),
    last_update=datetime.fromtimestamp(0)
)


def prompt_gpt4_start(prompt, chat_id):
    gpt4_prompt_job = state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=chat_id,
        prompt=prompt,
        tg_bot_token=SecretStr(os.getenv("TELEGRAM_BOT_TOKEN")),
        result_ttl=3600,
        retry=Retry(max=3, interval=[3, 5, 7])
    )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    msg_start = "GPT4 FastBot\n" \
                "\n" \
                "Ask me something. Or use cmd `/gen <something>`."
    await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=['gen'])
async def message_gen_cmd(message: types.Message):
    if len(message.text) < 5:
        await message.answer(f"The text is very short.")
        return
    prompt_gpt4_start(
        prompt=message.text[5:],  # remove '/gen ' from msg
        chat_id=message.chat.id
    )


@dp.message_handler()
async def all_message_handler(message: types.Message):
    prompt_gpt4_start(prompt=message.text, chat_id=message.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dp)
