import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import User
from app.responses import api_response, error_response
from app.routes.ai import router as ai_router
from app.routes.channels import router as channels_router
from app.routes.export import router as export_router
from app.routes.history import router as history_router
from app.schemas import APIEnvelope

logger = logging.getLogger(__name__)


def ensure_demo_user(db: Session) -> None:
    demo_user = db.get(User, settings.demo_user_id)
    if demo_user:
        return

    db.add(
        User(
            id=settings.demo_user_id,
            email=settings.demo_user_email,
            display_name=settings.demo_user_display_name,
        )
    )
    db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        try:
            ensure_demo_user(db)
        except Exception:
            db.rollback()
            raise

    try:
        yield
    finally:
        engine.dispose()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO(authentication): replace demo bootstrap + static user with JWT/Auth.js.
# TODO(billing): add usage metering and subscription checks at route/service layer.
# TODO(telegram): add Telegram bot webhook + orchestration endpoints.
# TODO(youtube): add YouTube Data API sync for channel stats and publishing workflows.
# TODO(multiplatform): expand content pipeline to TikTok and Instagram Reels.


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and {"success", "message", "data"}.issubset(exc.detail):
        content = exc.detail
    else:
        content = error_response(message=str(exc.detail or "Request failed"))
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", [])),
            "message": error.get("msg", "Invalid value"),
            "type": error.get("type", "validation_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(message="Validation failed", data={"errors": errors}),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="Database operation failed"),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="Internal server error"),
    )


@app.get("/health", response_model=APIEnvelope)
def health() -> dict:
    return api_response(
        message="CreatorFlow AI backend is healthy",
        data={
            "version": settings.app_version,
            "api_prefix": settings.api_prefix,
            "auto_create_tables": settings.auto_create_tables,
        },
    )


app.include_router(channels_router, prefix=settings.api_prefix, tags=["Channels"])
app.include_router(ai_router, prefix=settings.api_prefix, tags=["AI"])
app.include_router(history_router, prefix=settings.api_prefix, tags=["History"])
app.include_router(export_router, prefix=settings.api_prefix, tags=["Export"])
