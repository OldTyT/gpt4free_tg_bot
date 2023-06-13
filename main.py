import logging  # noqa F401
import logger  # noqa F401

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from rq import Retry
from loguru import logger as my_logger

from models.configs import GlobalConfigs
from jobs import GenerateTextWithGPTModel
from proxy import ProxyMessage

logging.getLogger().setLevel(logging.DEBUG)
cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())
dp = Dispatcher(bot)
pm = ProxyMessage()


def prompt_gpt4_start(prompt, chat_id):
    my_logger.debug(f"Setup gpt4_prompt_job. Chat id: {chat_id}. Prompt: {prompt}")
    cfg.state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=chat_id,
        prompt=prompt,
        tg_bot_token=cfg.telegram_token_bot,
        job_timeout=120,
        retry=Retry(max=3)
    )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if await pm.cmd_start(message):
        if await pm.check(message):
            msg_start = "GPT4 FastBot\n" \
                        "\n" \
                        "Ask me something. Or use cmd `/gen <something>`."
            await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=['ping'])
async def message_ping_cmd(message: types.Message):
    await message.answer("pong")


@dp.message_handler(commands=['gen'])
async def message_gen_cmd(message: types.Message):
    if await pm.check(message):
        if len(message.text) < 5:
            await message.answer("The text is very short.")
            return
        prompt_gpt4_start(
            prompt=message.text[5:],  # remove '/gen ' from msg
            chat_id=message.chat.id
        )


@dp.message_handler()
async def all_message_handler(message: types.Message):
    if await pm.check(message):
        prompt_gpt4_start(prompt=message.text, chat_id=message.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dp)
