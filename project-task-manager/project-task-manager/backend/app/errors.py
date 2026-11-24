from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Gabim i kontrolluar i aplikacionit: kod HTTP + kod i qëndrueshëm + mesazh."""

    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message


def error_response(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": error, "message": message},
    )


async def app_error_handler(request: Request, exc: AppError):
    return error_response(exc.status_code, exc.error, exc.message)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    # FastAPI kthen 422 si parazgjedhje; këtu kthehet 400 me formatin tonë (KJ-07)
    first = exc.errors()[0]
    field = ".".join(str(p) for p in first["loc"] if p not in ("body", "query", "path"))
    if first["type"] == "missing":
        message = f"{field} is required."
    elif field:
        message = f"{field}: {first['msg']}"
    else:
        message = first["msg"]
    return error_response(400, "VALIDATION_ERROR", message)


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    names = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return error_response(exc.status_code, names.get(exc.status_code, "HTTP_ERROR"), str(exc.detail))
