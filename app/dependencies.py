import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sentry_sdk import set_user
from starlette.requests import Request

from app.helpers.connection import get_db
from app.helpers.jwt import decode_jwt_token
from app.models.auth import RefreshToken
from app.services.crud import get_item
from app.services.users import get_user_by_id

oauth2_scheme = HTTPBearer()

logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request, token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db=Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt_token(token.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except Exception:
        logger.exception("Problems decoding JWT. [jwt=%s]", token.credentials)
        raise credentials_exception

    user = await get_user_by_id(user_id=user_id)
    if not user:
        logger.warning("User in JWT token not found. [user_id=%s]", user_id)
        raise credentials_exception

    # TODO: use cache for this
    refresh_token = await get_item(filters={"user": user.pk}, result_obj=RefreshToken, current_user=user)
    if not refresh_token:
        logger.warning("Refresh tokens have all been revoked. [user_id=%s]", user_id)
        raise credentials_exception

    request.state.user_id = user_id
    request.state.auth_type = "bearer"

    set_user({"id": user_id})

    return user


async def common_parameters(
    before: Optional[str] = None,
    after: Optional[str] = None,
    around: Optional[str] = None,
    limit: int = 50,
    sort_by_field: str = "created_at",
    sort_by_direction: int = -1,
):
    present = [v for v in [before, after, around] if v is not None]
    if len(present) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only one of 'before', 'after' and 'around can be present."
        )

    return {
        "before": before,
        "after": after,
        "around": around,
        "limit": limit,
        "sort_by_field": sort_by_field,
        "sort_by_direction": sort_by_direction,
    }
