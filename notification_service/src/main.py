# stdlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# thirdparty
import sentry_sdk
from admin import (
    PeriodicNotificationAdmin,
    ScheduledNotificationAdmin,
    TemplateAdmin,
)
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqladmin import Admin

# project
from api.v1 import api_router as api_v1_router
from core.config import settings
from db import redis
from db.db import engine
from handlers import exception_handlers
from middlewares.request_id import request_id_require
from services.rabbitmq import RabbitMQService

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    rabbitmq_service = RabbitMQService()
    await rabbitmq_service.init_queues()
    redis.redis = Redis.from_url(settings.redis_url)
    try:
        yield
    finally:
        if redis.redis is not None:
            await redis.redis.aclose()
        await rabbitmq_service.close()


app = FastAPI(
    title=settings.project_name,
    description="API сервис уведомлений",
    version="1.0.0",
    docs_url="/api-notify/openapi",
    openapi_url="/api-notify/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

admin = Admin(app, engine)
admin.add_view(TemplateAdmin)
admin.add_view(ScheduledNotificationAdmin)
admin.add_view(PeriodicNotificationAdmin)

app.middleware("http")(request_id_require)

app.include_router(api_v1_router, prefix="/api-notify/v1")
