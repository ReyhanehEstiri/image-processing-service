from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import users, images
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .limiter import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image Processing Service")

app.include_router(users.router)
app.include_router(images.router)


@app.get("/")
def home():
    return {"message": "Image service is running"}


@app.get("/health")
def health():
    return {"status": "ok"}