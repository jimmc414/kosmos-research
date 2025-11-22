"""Pydantic v1/v2 compatibility utilities.

This module provides compatibility wrappers to handle differences between
Pydantic v1 and v2, allowing the codebase to work with either version.
"""

from typing import Any, Dict


def model_to_dict(model: Any, **kwargs) -> Dict[str, Any]:
    """Convert Pydantic model to dictionary, compatible with v1 and v2.

    This function provides a unified interface for converting Pydantic models
    to dictionaries, handling both v1 (dict()) and v2 (model_dump()) APIs.

    Args:
        model: A Pydantic model instance or any object
        **kwargs: Additional arguments to pass to the conversion method
            (e.g., exclude_unset=True, by_alias=True)

    Returns:
        Dictionary representation of the model

    Examples:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        >>> user = User(name="Alice", age=30)
        >>> model_to_dict(user)
        {'name': 'Alice', 'age': 30}
    """
    # Try Pydantic v2 method first
    if hasattr(model, 'model_dump'):
        return model.model_dump(**kwargs)
    # Fall back to Pydantic v1 method
    elif hasattr(model, 'dict'):
        return model.dict(**kwargs)
    # Handle plain objects or dataclasses
    elif hasattr(model, '__dict__'):
        return dict(model.__dict__)
    # Last resort - try to convert directly
    else:
        try:
            return dict(model)
        except (TypeError, ValueError):
            # If all else fails, return empty dict
            return {}