import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

STATUS_CODE_NAMES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
}


def _envelope(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message, "request_id": f"req_{uuid.uuid4().hex[:12]}"}}


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = STATUS_CODE_NAMES.get(exc.status_code, "ERROR")
    return JSONResponse(status_code=exc.status_code, content=_envelope(code, str(exc.detail)))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first_error.get("loc", []))
    message = f"{first_error.get('msg', 'Invalid request')}: {field}".strip(": ")
    return JSONResponse(status_code=400, content=_envelope("VALIDATION_ERROR", message))
