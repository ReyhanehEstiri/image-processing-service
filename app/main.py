from fastapi import FastAPI

app = FastAPI(title="Image Processing Service")

@app.get("/")
def home():
    return {"message": "Image service is running"}
@app.get("/health")
def health():
    return {"status": "ok"}