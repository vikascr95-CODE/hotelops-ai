from fastapi import FastAPI

from app.routers import rooms, reservations, guests

app = FastAPI(title="HotelOps AI", version="0.1.0")
app.include_router(rooms.router)
app.include_router(guests.router)
app.include_router(
    guest_router,
    prefix="/api/v1",
    include_in_schema=False,
)

@app.get("/")
def home():
    return {"project": "HotelOps AI", "message": "Hotel operations API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
from app.routers import rooms, reservations     # add "reservations" to your existing import
...
app.include_router(reservations.router)         # add this under app.include_router(rooms.router)