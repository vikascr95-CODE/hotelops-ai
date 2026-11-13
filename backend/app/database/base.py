from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
from app.database.connection import Base  # noqa: F401