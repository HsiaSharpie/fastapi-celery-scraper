from fastapi import APIRouter

from . import tasks

news_router = APIRouter(prefix="/news", )