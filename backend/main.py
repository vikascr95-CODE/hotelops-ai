
from fastapi import FastAPI

app = FastAPI(
    title="HotelOps AI",
    description="Autonomous Hotel Operations and Intelligence Platform",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "project": "HotelOps AI",
        "message": "Welcome to HotelOps AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HotelOps AI Backend",
        "version": "0.1.0"
    }
