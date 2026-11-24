from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import config
from app.errors import (
    AppError,
    app_error_handler,
    http_error_handler,
    validation_error_handler,
)
from app.routes import auth, comments, dashboard, projects, tasks

app = FastAPI(title="Sistem për Menaxhimin e Projekteve dhe Detyrave")

# Lejon frontend-in (origjinë tjetër) ta thërrasë API-në nga shfletuesi
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
