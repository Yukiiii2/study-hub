from fastapi import APIRouter

from app.core.auth import CurrentUser
from app.schemas.auth import AuthenticatedUser

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=AuthenticatedUser)
def me(user: CurrentUser) -> AuthenticatedUser:
    return user
