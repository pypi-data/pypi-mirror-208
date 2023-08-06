from datetime import datetime as dt

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from plutous.models.mixin import BaseMixin


class Base(DeclarativeBase, BaseMixin):
    __table_args__ = (
        {"schema": "trade"},
    )

    exchange: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[int] = mapped_column(TIMESTAMP, nullable=False)
    datetime: Mapped[dt] = mapped_column(TIMESTAMP, nullable=False)
