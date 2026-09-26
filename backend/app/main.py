"""
main.py - LoanDefault MLBC FastAPI application entrypoint.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import database
from app.api import health, model, predictions, applications, dashboard, analytics, blockchain, export

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loan_default_mlbc")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.connect()
    try:
        database.ensure_indexes()
        logger.info("Connected to MongoDB and ensured indexes.")
    except Exception as e:
        logger.warning(f"Could not ensure MongoDB indexes at startup: {e}")
    yield
    database.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Machine Learning-Based Loan Default Risk Prediction and "
        "Blockchain-Based Loan Record Management System (academic demo). "
        + settings.ACADEMIC_DISCLAIMER
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})


app.include_router(health.router, prefix="/api")
app.include_router(model.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(blockchain.router, prefix="/api")
app.include_router(export.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "disclaimer": settings.ACADEMIC_DISCLAIMER,
    }
