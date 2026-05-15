import uvicorn
from fastapi import FastAPI

from app.api import router
from app.core import settings
from app.lifecycle import lifespan


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app")
