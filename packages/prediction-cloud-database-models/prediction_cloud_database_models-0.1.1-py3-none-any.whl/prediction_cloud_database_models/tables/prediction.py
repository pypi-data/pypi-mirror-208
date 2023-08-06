from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import DOUBLE

from .base import Base


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(DateTime, nullable=False)
    lower_interval = Column(DOUBLE, nullable=False)
    exchange_rate = Column(DOUBLE, nullable=False)
    upper_interval = Column(DOUBLE, nullable=False)
    symbol = Column(String(6), nullable=False)
