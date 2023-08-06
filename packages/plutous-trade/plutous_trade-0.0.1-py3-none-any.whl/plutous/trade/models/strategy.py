from sqlalchemy.orm import Mapped

from .base import Base


class Strategy(Base):
    name: Mapped[str]
    description: Mapped[str]