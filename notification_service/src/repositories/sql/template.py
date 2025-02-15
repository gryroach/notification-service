# thirdparty
from sqlalchemy.ext.asyncio import AsyncSession

# project
from models import Template
from repositories.sql.base import BaseCRUDRepository
from repositories.sql.interfaces.repositories import ITemplateRepository
from schemas.templates import TemplateCreate, TemplateUpdate


class TemplateRepository(
    BaseCRUDRepository[Template, TemplateCreate, TemplateUpdate],
    ITemplateRepository[Template, TemplateCreate, TemplateUpdate],
):
    """Репозиторий для работы с запланированными уведомлениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(Template, session)
