from fastapi import APIRouter

news_router = APIRouter(prefix="/news", )

from . import tasks