from fastapi import HTTPException

def http_error(status: int, code: str, message: str, details: dict | None=None):
    raise HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message, "details": details or {}}}
    )