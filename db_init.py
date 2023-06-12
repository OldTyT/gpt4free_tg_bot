import asyncio

import typer

from loguru import logger
from db.base import init_models
from models.users import Users  # noqa: F401
from models.history import MessageHistory  # noqa: F401

cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    logger.info("Table created")


if __name__ == '__main__':
    cli()
