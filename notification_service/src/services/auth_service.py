# stdlib
import random
from datetime import date
from uuid import uuid4

# project
from core.config import settings
from schemas.auth_service import UserData


class AuthServiceBase:
    async def get_users(
        self,
        birth_month: int | None = None,
        birth_day: int | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> list[dict]:
        raise NotImplementedError

    @staticmethod
    async def get_user_data(user_id: str) -> UserData:
        raise NotImplementedError


class AuthMockService(AuthServiceBase):
    """Заглушка сервиса аутентификации для тестирования"""

    def __init__(self) -> None:
        self.users: list[dict] = []
        self._populate_mock_data()

    def _populate_mock_data(self) -> None:
        """Генерация тестовых пользователей"""
        for i in range(1, 1001):
            self.users.append(
                {
                    "id": uuid4(),
                    "birth_date": date(
                        1990 + i % 30,
                        random.randint(1, 12),
                        random.randint(1, 28),
                    ),
                }
            )

    async def get_users(
        self,
        birth_month: int | None = None,
        birth_day: int | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> list[dict]:
        """Имитация поиска пользователей с пагинацией"""
        if birth_month and not 1 <= birth_month <= 12:  # noqa: PLR2004
            raise ValueError("Invalid birth month")

        if birth_day and not 1 <= birth_day <= 31:  # noqa: PLR2004
            raise ValueError("Invalid birth day")

        filtered = [
            u
            for u in self.users
            if (not birth_month or u["birth_date"].month == birth_month)
            and (not birth_day or u["birth_date"].day == birth_day)
        ]

        start = (page - 1) * page_size
        end = start + page_size
        return filtered[start:end]

    @staticmethod
    async def get_user_data(user_id: str) -> UserData:
        return UserData(
            id=user_id,
            birth_date=date(
                random.randint(1900, 2022),
                random.randint(1, 12),
                random.randint(1, 28),
            ),
            email=f"{user_id}@{random.choice(['gmail.com', 'mail.ru', 'yandex.ru'])}",
            first_name=random.choice(["John", "Oliver", "Emma", "Noah", "Liam"]),
            last_name=random.choice(["Doe", "Smith", "Johnson", "Williams", "Jones"]),
            phone=(
                f"+7 ({random.randint(100, 999)}) "
                f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            ),
            avatar=f"https://example.com/{random.randint(1, 1000)}.jpg",
        )


auth_service: AuthServiceBase
if settings.mock_auth_service:
    auth_service = AuthMockService()
else:
    auth_service = AuthServiceBase()
