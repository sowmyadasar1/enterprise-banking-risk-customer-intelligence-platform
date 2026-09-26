"""FastAPI dependency injection module."""

from typing import Generator, Any


def get_db() -> Generator[Any, None, None]:
    """Dependency for providing database sessions."""
    raise NotImplementedError("Implemented in Phase N")
    yield None


def get_model_registry() -> Any:
    """Dependency for providing the model registry."""
    raise NotImplementedError("Implemented in Phase N")
