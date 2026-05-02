from typing import Any

from fastapi.encoders import jsonable_encoder


def api_response(*, message: str, data: dict[str, Any] | None = None, success: bool = True) -> dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": jsonable_encoder(data or {}),
    }


def error_response(*, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return api_response(success=False, message=message, data=data)

