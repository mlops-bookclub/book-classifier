import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.routers import books, health, recommend

logger = logging.getLogger(__name__)

_MAX_REQUEST_BODY_BYTES = 10_240  # 10 KB


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose Content-Length header exceeds the configured limit."""

    async def dispatch(self, request: Request, call_next: object) -> JSONResponse:
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                size = int(content_length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
            if size > _MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
        return await call_next(request)  # type: ignore[arg-type]


app = FastAPI(
    title="Book Recommender API",
    description="Inference API for the Book Recommender service",
    version="0.1.0",
)

app.add_middleware(BodySizeLimitMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(health.router)
app.include_router(books.router)
app.include_router(recommend.router)
