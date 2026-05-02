"""Schema validation helpers."""

from __future__ import annotations

from pydantic import BaseModel, ValidationError


def validate_against_model(data: dict, model_class: type[BaseModel]) -> BaseModel:
    """Validate a dict against a Pydantic model.

    Args:
        data: Raw dict to validate.
        model_class: Pydantic model class.

    Returns:
        Validated model instance.

    Raises:
        ValidationError: If validation fails.
    """
    return model_class(**data)


def safe_validate(data: dict, model_class: type[BaseModel]) -> tuple[BaseModel | None, str]:
    """Attempt validation, returning (instance, error_message).

    Args:
        data: Raw dict to validate.
        model_class: Pydantic model class.

    Returns:
        Tuple of (model_instance, error_message).
        error_message is empty string on success.
    """
    try:
        return model_class(**data), ""
    except ValidationError as exc:
        return None, str(exc)
