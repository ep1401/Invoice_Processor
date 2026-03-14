from fastapi import FastAPI

from app.api.routes import router
from app.config import ensure_directories


def create_app() -> FastAPI:
    ensure_directories()

    app = FastAPI(
        title="Invoice Tax Service",
        version="1.0.0",
        description="Processes invoice PDFs, extracts structured line items, calculates tax, and persists results.",
    )

    app.include_router(router)

    return app


app = create_app()