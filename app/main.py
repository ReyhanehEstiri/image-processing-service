from fastapi import FastAPI
from .database import Base, engine
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image Processing Service")

@app.get("/")
def home():
    return {"message": "Image service is running"}

@app.get("/health")
def health():
    return {"status": "ok"}