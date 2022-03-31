from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from project import config

engine = create_engine(config.settings.DATABASE_URL,
                       connect_args=config.settings.DATABASE_CONNECT_DICT)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# # dependency
# def get_db():
#     db = SessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()