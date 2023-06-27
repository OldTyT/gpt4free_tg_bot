from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import BigInteger

from db.base import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
