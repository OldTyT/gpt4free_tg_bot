import logging  # noqa F401
import random
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from loguru import logger as my_logger
from redis import Redis
from rq import Queue, Retry

import logger  # noqa F401
from jobs import GenerateTextWithGPTModel
from models.configs import GlobalConfigs
from models.runtime import RuntimeSettings
from proxy import ProxyCallbackQuery, ProxyMessage

logging.getLogger().setLevel(logging.DEBUG)
cfg = GlobalConfigs()
bot = Bot(token=cfg.telegram_token_bot.get_secret_value())
dp = Dispatcher(bot)
pm = ProxyMessage()
pcb = ProxyCallbackQuery()


redis_conn = Redis(
    host=cfg.redis_host,
    password=cfg.redis_password.get_secret_value(),
    port=cfg.redis_port,
    db=cfg.redis_db,
)

state_cfg = RuntimeSettings(
    redis_conn=redis_conn,
    rq_queue=Queue("fast_gpt4_bot_queue", connection=redis_conn),
    started_at=datetime.now(timezone.utc),
    last_update=datetime.fromtimestamp(0),
)

prompt_callback = CallbackData("prompt", "something")


def get_rnd_prompt() -> str:
    """Return a random prompt from a list."""
    prompt_list = [
        "What is the weather like?",
        "How old is Elon Musk?",
        "Translate 'hello' to Spanish.",
        "What's the capital of France?",
        "Who won the last Super Bowl?",
        "What's the time in Tokyo?",
        "How do I make pancakes?",
        "What's the population of New York?",
        "What's the price of Bitcoin?",
        "What's the meaning of 'serendipity'",
    ]
    return prompt_list[random.randint(0, len(prompt_list) - 1)]  # noqa: S311


def prompt_gpt4_start(prompt, chat_id, msg_id):
    """Put a task in a queue for text generate."""
    my_logger.debug(f"Setup gpt4_prompt_job. Chat id: {chat_id}. Prompt: {prompt}")
    state_cfg.rq_queue.enqueue(
        GenerateTextWithGPTModel,
        chat_id=chat_id,
        prompt=prompt,
        msg_id=msg_id,
        job_timeout=300,
        retry=Retry(max=5, interval=1),
    )


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    """Process start command."""
    if await pm.cmd_start(message):
        if await pm.check(message):
            await dp.bot.set_my_commands(
                [
                    types.BotCommand("gen", "Text generation. Ex.: /gen <something>"),
                    types.BotCommand("help", "Help"),
                    types.BotCommand("ping", "Pong"),
                ]
            )
            msg_start = (
                "Hello! I'm fastest GPT bot\n"
                "\n"
                f"Ask me '{get_rnd_prompt()}'. Or use cmd `/gen {get_rnd_prompt()}`.\n"
                "Send command - `/help` for more info"
            )
            await message.answer(msg_start, parse_mode="Markdown")


@dp.message_handler(commands=["help"])
async def message_help_cmd(message: types.Message):
    """Process help command."""
    if await pm.check(message):
        username = (await bot.get_me()).username
        msg_help = (
            "*Text generate*\n"
            f"┣`/gen {get_rnd_prompt()}`\n"
            "┃ or use only in private messages:\n"
            f"┗`{get_rnd_prompt()}`\n"
            "\n"
            "*Inline mode*\n"
            "┃ bot support text generate from inline mode\n"
            f"┗`@{username} {get_rnd_prompt()}`\n"
            "\n"
            "*Other*\n"
            "┗`/ping` - Pong\n"
        )
        await message.answer(msg_help, parse_mode="Markdown")


@dp.message_handler(commands=["ping"])
async def message_ping_cmd(message: types.Message):
    """Ping pong."""
    await message.answer("pong")


@dp.message_handler(commands=["gen"])
async def message_gen_cmd(message: types.Message):
    """Receiving messages by the gen command."""
    if await pm.check(message):
        if message.text.find(" ") == -1:
            await message.answer("The text is very short.")
            return
        prompt = message.text[message.text.find(" ") + 1:]  # remove '/gen ' from msg
        if len(prompt) < 1:
            await message.answer("The text is very short.")
            return
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(prompt=prompt, chat_id=message.chat.id, msg_id=msg_id)


@dp.message_handler()
async def all_message_handler(message: types.Message):
    """Receiving all messages."""
    if await pm.check(message):
        if message.chat.id != message.from_user.id:  # Checking if chat type is private
            return
        msg_id = await message.answer("Wait please...")
        msg_id = msg_id.message_id
        prompt_gpt4_start(prompt=message.text, chat_id=message.chat.id, msg_id=msg_id)


@dp.inline_handler()
async def inline_general_handler(inline_query: InlineQuery):
    """General process inline."""
    prompt = inline_query.query or "something"
    prompt_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Generate",
                    callback_data=prompt_callback.new(
                        prompt,
                    ),
                ),
            ]
        ]
    )
    item = InlineQueryResultArticle(
        id=1,
        description="Send message for generate text from this prompt.",
        title=prompt,
        reply_markup=prompt_kb,
        input_message_content=InputTextMessageContent(
            "Please click on the button.", parse_mode=types.ParseMode.HTML
        ),
    )
    await bot.answer_inline_query(
        inline_query.id,
        results=[item],
        cache_time=1,
        switch_pm_parameter="from_inline_prompt_generate",
        switch_pm_text="Back to bot.",
    )


@dp.callback_query_handler(prompt_callback.filter())
async def process_callback_prompt_generate(callback_query: types.CallbackQuery):
    """Process callback query prompt."""
    if await pcb.check(callback_query):
        prompt = callback_query.data[callback_query.data.find(":") + 1:]
        prompt_gpt4_start(
            prompt=prompt, chat_id=0, msg_id=callback_query.inline_message_id
        )
        await bot.edit_message_text(
            inline_message_id=callback_query.inline_message_id,
            text="Please wait...",
            parse_mode=types.ParseMode.HTML,
        )


if __name__ == "__main__":
    executor.start_polling(dp)
