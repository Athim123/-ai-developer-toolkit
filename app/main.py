from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import auth, evaluate, projects, prompts, retrieval, runs, tools
from app.core.database import init_db
from app.core.errors import http_exception_handler, validation_exception_handler
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="AI Developer Toolkit API",
    version="0.1.0",
    description="Unified prompt, orchestration, tool, evaluation, and retrieval API. LLM provider: Groq.",
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(prompts.router)
app.include_router(runs.router)
app.include_router(tools.router)
app.include_router(evaluate.router)
app.include_router(retrieval.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
