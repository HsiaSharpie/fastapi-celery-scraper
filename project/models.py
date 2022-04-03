from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

from project.database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    rapper = Column(String, nullable=False)
    source = Column(String, nullable=True)
    post_time = Column(String, nullable=True)
    # post_time = Column(TIMESTAMP(timezone=True), nullable=True)
    origin_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    related_rapper_id = Column(Integer,
                               ForeignKey("rapper.id", ondelete="CASCADE"),
                               nullable=False)


class Rapper(Base):
    __tablename__ = "rapper"

    id = Column(Integer, primary_key=True, nullable=False)
    rap_name = Column(String, nullable=False)
