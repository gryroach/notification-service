# stdlib
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

# project
from services.auth_service import auth_service
from services.subscriber_resolver import SubscriberResolver


@SubscriberResolver.register("birthday_today")
async def fetch_birthday_users(params: dict[str, Any], batch_size: int) -> AsyncGenerator[list[str], None]:
    page = 1
    while True:
        users = await auth_service.get_users(
            birth_month=datetime.now().month,
            birth_day=datetime.now().day,
            page=page,
            page_size=batch_size,
        )
        if not users:
            break
        yield [str(u["id"]) for u in users]
        page += 1
