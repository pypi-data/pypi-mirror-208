from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import text
from sqlalchemy import Enum
from sqlalchemy.sql import func

from .base import Base
from prediction_cloud_database_models.enums import Role


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    confirmed = Column(Boolean, nullable=False, server_default=text('false'))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    role = Column(Enum(Role), nullable=False)
    registration_date = Column(DateTime, nullable=False, server_default=func.now())
    last_login = Column(DateTime, nullable=True, server_default=None)
    tutorial = Column(String(20), nullable=False)
