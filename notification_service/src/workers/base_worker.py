# stdlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

# thirdparty
from arq.worker import CronJob

# project
from core.config import settings

CRON_ARGS = 5


@dataclass
class BaseTask:
    name: str
    function: str
    coroutine: Callable[..., Awaitable[None]]
    cron_schedule: str

    def as_cron_job(self) -> CronJob:
        return create_cron_job(
            name=self.name,
            coroutine=self.coroutine,
            cron_schedule=self.cron_schedule,
        )


def parse_cron_field(value: str) -> int | None:
    return None if value == "*" else int(value)


def create_cron_job(
    name: str,
    coroutine: Callable[..., Awaitable[None]],
    cron_schedule: str,
    **kwargs: Any,
) -> CronJob:
    cron_parts = cron_schedule.split()
    if len(cron_parts) != CRON_ARGS:
        raise ValueError(f"Invalid cron schedule format: {cron_schedule}")

    return CronJob(
        name=name,
        coroutine=coroutine,  # type: ignore
        month=parse_cron_field(cron_parts[3]),
        day=parse_cron_field(cron_parts[2]),
        weekday=parse_cron_field(cron_parts[4]),
        hour=parse_cron_field(cron_parts[1]),
        minute=parse_cron_field(cron_parts[0]),
        second=0,
        microsecond=0,
        unique=True,
        job_id=None,
        run_at_startup=True,
        timeout_s=settings.arq_job_timeout,
        keep_result_s=settings.arq_job_keep_result,
        keep_result_forever=False,
        max_tries=3,
        **kwargs,
    )
