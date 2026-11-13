from fastapi import FastAPI
from app.routers import rooms

app = FastAPI(title="HotelOps AI")
app.include_router(rooms.router)


@app.get("/health")
def health():
    return {"status": "ok"}