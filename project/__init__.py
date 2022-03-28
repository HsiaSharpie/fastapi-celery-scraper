from fastapi import FastAPI
from project import models, database, celery_utils


def create_app() -> FastAPI:
    app = FastAPI()

    # do this before loading routes
    app.celery_app = celery_utils.create_celery()

    from project.rapper import rapper_router
    from project.news import news_router

    app.include_router(rapper_router)
    app.include_router(news_router)

    # sqlalchemy will create the table if it doesn't exist
    models.Base.metadata.create_all(bind=database.engine)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app
