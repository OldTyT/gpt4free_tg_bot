"""History models for: messages in chats, chats, callbackquery."""

from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSON

from db.base import Base


class Chats(Base):
    """Model for save chats, with message_count and other params."""

    __tablename__ = "chats"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)  # noqa: A003
    chat_id = Column(BigInteger, nullable=False)
    message_last_time = Column(DateTime(timezone=True), nullable=False)
    message_count = Column(Integer, nullable=False)


class MessageHistory(Base):
    """Model for save messages is json."""

    __tablename__ = "message_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)  # noqa: A003
    message = Column(JSON, nullable=False)


class CallbackQueryHistory(Base):
    """Model for save callbackquery is json."""

    __tablename__ = "callback_query_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)  # noqa: A003
    callback_query = Column(JSON, nullable=False)
