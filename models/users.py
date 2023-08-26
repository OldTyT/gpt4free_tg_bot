"""Class users for save user in table."""
from sqlalchemy import BigInteger, Column, Integer, String

from db.base import Base


class Users(Base):
    """Class users for save user in table."""

    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)  # noqa: A003
    user_id = Column(BigInteger, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
