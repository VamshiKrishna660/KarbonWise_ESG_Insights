from fastapi import Header, HTTPException, status
from app.config import get_settings

settings = get_settings()


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Dependency that validates the X-API-Key header."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key.",
        )
    return x_api_key
