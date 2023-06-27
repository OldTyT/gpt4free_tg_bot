from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import JSON

from db.base import Base


class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    chat_id = Column(BigInteger, nullable=False)
    message_last_time = Column(DateTime(timezone=True), nullable=False)
    message_count = Column(Integer, nullable=False)


class MessageHistory(Base):
    __tablename__ = "message_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    message = Column(JSON, nullable=False)


class CallbackQueryHistory(Base):
    __tablename__ = "callback_query_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    callback_query = Column(JSON, nullable=False)
