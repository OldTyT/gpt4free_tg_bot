import asyncio
import logging  # noqa F401

import logger  # noqa F401
import typer

from loguru import logger as my_logger
from db.base import init_models
from models.users import Users  # noqa: F401
from models.history import MessageHistory, CallbackQueryHistory, Chats  # noqa: F401

cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    my_logger.info("Table created")


if __name__ == '__main__':
    cli()
