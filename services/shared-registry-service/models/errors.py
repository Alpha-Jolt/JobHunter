"""Error response helpers."""


def not_found(resource: str, resource_id: str) -> dict:
    return {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": f"{resource} '{resource_id}' not found",
            "status": 404,
        }
    }


def already_exists(message: str) -> dict:
    return {"error": {"code": "ALREADY_EXISTS", "message": message, "status": 409}}


def validation_error(message: str) -> dict:
    return {"error": {"code": "VALIDATION_ERROR", "message": message, "status": 400}}
