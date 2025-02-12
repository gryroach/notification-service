# thirdparty
from fastapi import APIRouter

from .messages import router as messages_router

api_router = APIRouter()

api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
