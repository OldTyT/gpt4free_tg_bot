"""Create tables with typer."""
import asyncio
import logging  # noqa F401

import typer
from loguru import logger as my_logger

import logger  # noqa F401
from db.base import init_models
from models.history import (CallbackQueryHistory, Chats,  # noqa: F401
                            MessageHistory)
from models.users import Users  # noqa: F401

cli = typer.Typer()


@cli.command()
def db_init_models():
    """Create tables with typer."""
    asyncio.run(init_models())
    my_logger.info("Table created")


if __name__ == "__main__":
    cli()
