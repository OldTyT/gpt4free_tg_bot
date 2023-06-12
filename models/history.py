from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSON

from db.base import Base


class MessageHistory(Base):
    __tablename__ = "message_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    message = Column(JSON)
