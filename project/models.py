from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

from project.database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=True)
    post_time = Column(TIMESTAMP(timezone=True), nullable=True)
    origin_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    # rapper_id = Column(Integer,
    #                    ForeignKey("rapper.id", ondelete="CASCADE"),
    #                    nullable=False)
