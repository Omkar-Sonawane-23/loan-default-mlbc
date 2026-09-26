"""Shared FastAPI dependencies."""
from app.database import database


def get_database():
    return database.db
