# thirdparty
from schemas.templates import CreateTemplate, UpdateTemplate
from sqlalchemy.ext.asyncio import AsyncSession

# project
from models import Template
from repositories.sql.base import BaseCRUDRepository
from repositories.sql.interfaces.repositories import ITemplateRepository


class TemplateRepository(
    BaseCRUDRepository[Template, CreateTemplate, UpdateTemplate],
    ITemplateRepository[Template, CreateTemplate, UpdateTemplate],
):
    """Репозиторий для работы с запланированными уведомлениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(Template, session)
