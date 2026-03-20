from pydantic import BaseModel
from fastapi import HTTPException
from typing import Any


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


def http_error(status: int, code: str, message: str,
               details: dict | None = None) -> None:
    raise HTTPException(
        status_code=status,
        detail=ErrorEnvelope(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details or {}
            )
        ).model_dump()
    )
