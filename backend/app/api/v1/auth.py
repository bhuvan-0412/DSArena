from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_current_supabase_user

router = APIRouter()

@router.post("/sync", response_model=UserResponse)
def sync_supabase_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Sync/Upsert a Supabase user with the local database.
    Called on user login/auth callback to guarantee a single profile record.
    """
    db_user = db.query(User).filter(User.clerk_id == user_in.clerk_id).first()
    if not db_user:
        # Check by email as fallback to avoid duplicate email constraint
        db_user = db.query(User).filter(User.email == user_in.email).first()

    if db_user:
        db_user.clerk_id = user_in.clerk_id
        db_user.email = user_in.email
        if user_in.username:
            db_user.username = user_in.username
        if user_in.display_name:
            db_user.display_name = user_in.display_name
        if user_in.avatar_url:
            db_user.avatar_url = user_in.avatar_url
        db.commit()
        db.refresh(db_user)
        return db_user

    # Create new user profile
    new_user = User(
        clerk_id=user_in.clerk_id,
        email=user_in.email,
        username=user_in.username or user_in.email.split("@")[0],
        display_name=user_in.display_name or user_in.username or user_in.email.split("@")[0],
        avatar_url=user_in.avatar_url,
        xp=0,
        level=1,
        rank="Unranked",
        current_streak=0,
        max_streak=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
def get_current_authenticated_user(current_user: User = Depends(get_current_supabase_user)):
    """
    Returns the currently authenticated user based on validated Supabase JWT token.
    """
    return current_user
