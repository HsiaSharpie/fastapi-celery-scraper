from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class News(BaseModel):
    source: Optional[str] = None
    post_time: datetime
    origin_url: str
    title: str