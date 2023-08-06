from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from .base import Base


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    comment = Column(String(100), nullable=True)
    date = Column(DateTime, nullable=False, server_default=func.now())
    feelings = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
