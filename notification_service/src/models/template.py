# thirdparty
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

# project
from src.models.base import Base


class Template(Base):
    """Модель шаблона уведомления."""

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
