
from fastapi import FastAPI

from app.api.guest_routes import router as guest_router
from app.api.room_routes import router as room_router

app = FastAPI(
    title="HotelOps AI",
    description="Autonomous Hotel Operations and Intelligence Platform",
    version="1.0.0",
)

# Register API routers
app.include_router(guest_router)
app.include_router(room_router)


@app.get("/", tags=["Home"])
def home():
    return {
        "project": "HotelOps AI",
        "message": "Welcome to HotelOps AI",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "HotelOps AI Backend",
        "version": "1.0.0",
    }
