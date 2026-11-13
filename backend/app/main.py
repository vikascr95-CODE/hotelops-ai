from fastapi import FastAPI

from app.routers import rooms

app = FastAPI(title="HotelOps AI", version="0.1.0")
app.include_router(rooms.router)


@app.get("/")
def home():
    return {"project": "HotelOps AI", "message": "Hotel operations API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}