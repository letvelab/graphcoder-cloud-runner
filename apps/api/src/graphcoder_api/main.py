from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="GraphCoder Cloud Runner API",
        version="0.1.0",
        description="API service for submitting and tracking GraphCoder jobs.",
    )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="graphcoder-api",
            version="0.1.0",
        )

    return app


app = create_app()
