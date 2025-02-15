# stdlib
from typing import Any, Generic, TypeVar
from uuid import UUID

# thirdparty
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# project
from exceptions.db import ForeignKeyNotExistsError
from models.base import Base
from repositories.sql.interfaces.repositories import (
    IReadRepository,
    IWriteRepository,
)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUDRepository(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
    IReadRepository[ModelType],
    IWriteRepository[ModelType, CreateSchemaType, UpdateSchemaType],
):
    """Базовый класс для CRUD операций."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Создает новую запись в БД."""
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        try:
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.session.rollback()
            if "foreign key constraint" in str(e):
                raise ForeignKeyNotExistsError("Указанная связанная запись не существует")
            raise e

    async def get(self, id: UUID) -> ModelType | None:
        """Получает запись по ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Получает список записей с пагинацией."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        """Обновляет запись в БД."""
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        try:
            await self.session.commit()
            await self.session.refresh(db_obj)
        except IntegrityError as e:
            await self.session.rollback()
            if "foreign key constraint" in str(e):
                raise ForeignKeyNotExistsError("Указанная связанная запись не существует")
            raise e
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """Удаляет запись по ID."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """Получает запись по указанному полю."""
        query = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field_multi(
        self,
        field: str,
        value: Any,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Получает список записей по указанному полю с пагинацией."""
        query = select(self.model).where(getattr(self.model, field) == value).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
