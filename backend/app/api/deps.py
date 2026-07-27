from typing import Optional
import time
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.api.v1.users import get_or_create_user

def get_current_supabase_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates Supabase JWT Bearer token from request Authorization header.
    If valid, resolves or creates the matching local User record.
    Falls back gracefully to mock user in dev/demo mode when token is absent.
    """
    if not authorization or not authorization.startswith("Bearer "):
        # Dev/Demo fallback user when no token is passed
        return get_or_create_user(db, "mock_user_striver", email="striver@dsarena.com")

    token = authorization.split(" ")[1]

    try:
        import jwt

        # If Supabase JWT Secret is provided, decode and verify signature
        if settings.SUPABASE_JWT_SECRET:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        else:
            # Unverified decode when JWT secret is not configured in local environment
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_aud": False}
            )

        sub = payload.get("sub")
        email = payload.get("email", "")
        exp = payload.get("exp")
        user_metadata = payload.get("user_metadata", {})
        avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture", "")

        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Supabase token payload: missing sub claim"
            )

        if exp and exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Supabase session has expired"
            )

        return get_or_create_user(db, sub, email=email, avatar_url=avatar_url)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signature has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase JWT token: {str(e)}"
        )
    except Exception as e:
        print(f"Supabase JWT validation error: {e}")
        # In fallback local dev mode, parse prefix sub
        sub_fallback = token[:36] if len(token) >= 36 else "mock_user_striver"
        return get_or_create_user(db, sub_fallback, email="striver@dsarena.com")

# Alias for route dependency injection
get_current_user = get_current_supabase_user
