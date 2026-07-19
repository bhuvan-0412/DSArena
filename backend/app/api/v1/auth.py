from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/sync", response_model=UserResponse)
def sync_clerk_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Sync a Clerk user with the local database.
    Called when a user signs up or logs in for the first time.
    """
    db_user = db.query(User).filter(User.clerk_id == user_in.clerk_id).first()
    if db_user:
        # Update existing user email/username if changed
        db_user.email = user_in.email
        if user_in.username:
            db_user.username = user_in.username
        if user_in.display_name:
            db_user.display_name = user_in.display_name
        db.commit()
        db.refresh(db_user)
        return db_user

    # Create new user
    new_user = User(
        clerk_id=user_in.clerk_id,
        email=user_in.email,
        username=user_in.username or user_in.email.split("@")[0],
        display_name=user_in.display_name or user_in.username or user_in.email.split("@")[0],
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
