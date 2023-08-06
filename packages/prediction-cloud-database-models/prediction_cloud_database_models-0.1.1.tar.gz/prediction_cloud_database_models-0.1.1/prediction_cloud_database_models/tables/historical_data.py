from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import DOUBLE

from .base import Base


class HistoricalData(Base):
    __tablename__ = 'historical_data'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(DateTime, nullable=False)
    exchange_rate = Column(DOUBLE, nullable=False)
    symbol = Column(String(6), nullable=False)
