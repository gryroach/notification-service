# stdlib
import random
from datetime import date
from uuid import uuid4


class AuthMockService:
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


auth_service = AuthMockService()
