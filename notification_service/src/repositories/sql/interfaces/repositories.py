# stdlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

# thirdparty
from pydantic import BaseModel

# project
from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class IReadRepository(Generic[ModelType], ABC):
    """Базовый интерфейс для чтения данных."""

    @abstractmethod
    async def get(self, id: UUID) -> ModelType | None:
        """Получает запись по ID."""
        pass

    @abstractmethod
    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Получает список записей с пагинацией."""
        pass

    @abstractmethod
    async def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """Получает запись по указанному полю."""
        pass

    @abstractmethod
    async def get_by_field_multi(
        self,
        field: str,
        value: Any,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Получает список записей по указанному полю с пагинацией."""
        pass


class IWriteRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Базовый интерфейс для записи данных."""

    @abstractmethod
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Создает новую запись."""
        pass

    @abstractmethod
    async def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType | None:
        """Обновляет существующую запись."""
        pass

    @abstractmethod
    async def delete(self, *, id: UUID) -> bool:
        """Удаляет запись."""
        pass


class ITemplateRepository(
    IReadRepository[ModelType],
    IWriteRepository[ModelType, CreateSchemaType, UpdateSchemaType],
    ABC,
):
    """Интерфейс репозитория шаблонов."""

    pass


class IPeriodicNotificationRepository(
    IReadRepository[ModelType],
    IWriteRepository[ModelType, CreateSchemaType, UpdateSchemaType],
    ABC,
):
    """Интерфейс репозитория периодических уведомлений."""

    @abstractmethod
    async def get_pending(self, current_time: datetime) -> list[ModelType]:
        """Получает список активных уведомлений для выполнения."""
        pass

    @abstractmethod
    async def get_by_ids(self, ids: list[UUID]) -> list[ModelType]:
        """Получает список уведомлений по их ID."""
        pass


class IScheduledNotificationRepository(
    IReadRepository[ModelType],
    IWriteRepository[ModelType, CreateSchemaType, UpdateSchemaType],
    ABC,
):
    """Интерфейс репозитория запланированных уведомлений."""

    @abstractmethod
    async def get_pending(
        self,
        current_time: datetime,
        limit: int | None = None,
    ) -> list[ModelType]:
        """Получает список уведомлений, готовых к отправке."""
        pass

    @abstractmethod
    async def get_by_ids(self, ids: list[UUID]) -> list[ModelType]:
        """Получает список уведомлений по их ID."""
        pass
