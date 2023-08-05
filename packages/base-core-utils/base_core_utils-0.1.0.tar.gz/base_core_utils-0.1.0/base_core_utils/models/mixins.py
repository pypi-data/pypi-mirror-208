from datetime import datetime

from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.orm import Mapped


class TimestampMixin:
    created_at: Mapped[datetime] = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(TIMESTAMP, nullable=True, default=None, onupdate=datetime.utcnow)


class SoftDeleteMixin:
    deleted_at: Mapped[datetime] = Column(TIMESTAMP, nullable=True, default=None)
