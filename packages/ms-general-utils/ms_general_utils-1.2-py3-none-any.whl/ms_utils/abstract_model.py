"""
Abstract Base Model
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer


class BaseModel:
    """
    Datetime created_at and updated_at
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
