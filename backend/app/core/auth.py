from typing import Annotated

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.schemas.auth import AuthenticatedUser

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    unauthorized = HTTPException(
        status_code=401,
        detail="A valid signed-in session is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    key = settings.supabase_service_role_key.get_secret_value()
    if not settings.supabase_url or not key:
        raise HTTPException(status_code=503, detail="Authentication is not configured.")

    # Supabase verifies the token. Never trust unverified JWT claims or a body user_id.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={"apikey": key, "Authorization": f"Bearer {credentials.credentials}"},
            )
    except (httpx.RequestError, httpx.InvalidURL):
        raise HTTPException(status_code=503, detail="Authentication service is unavailable.") from None

    if response.status_code in (401, 403):
        raise unauthorized
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable.")
    try:
        return AuthenticatedUser.model_validate(response.json())
    except ValueError:
        raise HTTPException(status_code=503, detail="Authentication service returned an invalid response.") from None


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
