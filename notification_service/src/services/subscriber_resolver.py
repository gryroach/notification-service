# stdlib
from collections.abc import AsyncGenerator, Callable
from typing import Any, ClassVar, Protocol


class SubscriberFetcher(Protocol):
    def __call__(self, params: dict[str, Any], batch_size: int) -> AsyncGenerator[list[str], None]: ...


class SubscriberResolver:
    _fetchers: ClassVar[dict[str, SubscriberFetcher]] = {}

    @classmethod
    def register(cls, query_type: str) -> Callable[[SubscriberFetcher], SubscriberFetcher]:
        def decorator(func: SubscriberFetcher) -> SubscriberFetcher:
            cls._fetchers[query_type] = func
            return func

        return decorator

    async def resolve(
        self, query_type: str, params: dict[str, Any], batch_size: int = 100
    ) -> AsyncGenerator[list[str], None]:
        if query_type not in self._fetchers:
            raise ValueError(f"Unknown subscriber query type: {query_type}")

        generator = self._fetchers[query_type](params, batch_size)
        async for batch in generator:
            yield batch
