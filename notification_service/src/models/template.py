# stdlib
from uuid import UUID

# thirdparty
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

# project
from models.base import Base


class Template(Base):
    """Модель шаблона уведомления."""

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    staff_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
