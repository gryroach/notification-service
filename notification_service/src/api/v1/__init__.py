# thirdparty
from fastapi import APIRouter

from .messages import router as messages_router
from .periodic_notifications import router as periodic_notifications_router
from .scheduled_notifications import router as scheduled_notifications_router
from .sockets import router as sockets_router
from .templates import router as templates_router

api_router = APIRouter()

api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
api_router.include_router(periodic_notifications_router, prefix="/periodic", tags=["periodic"])
api_router.include_router(scheduled_notifications_router, prefix="/scheduled", tags=["scheduled"])
api_router.include_router(templates_router, prefix="/templates", tags=["templates"])
api_router.include_router(sockets_router, prefix="/sockets", tags=["web sockets"])
