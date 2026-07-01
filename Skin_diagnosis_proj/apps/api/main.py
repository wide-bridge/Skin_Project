from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Skin Diagnosis API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["null", "http://127.0.0.1:8010", "http://localhost:8010"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
