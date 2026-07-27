"""
DSArena Backend Persistence & Domain Services Layer
Provides structured service classes for clean database / Supabase data access.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User

class ProfileService:
    @staticmethod
    def get_profile(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.clerk_id == user_id).first()

    @staticmethod
    def upsert_profile(db: Session, user_id: str, email: str, display_name: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
        user = db.query(User).filter(User.clerk_id == user_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                clerk_id=user_id,
                email=email,
                username=user_id.replace("user_", "").replace("mock_user_", ""),
                display_name=display_name or "Gladiator",
                avatar_url=avatar_url
            )
            db.add(user)
        else:
            user.clerk_id = user_id
            user.email = email
            if display_name: user.display_name = display_name
            if avatar_url: user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user


class ProgressService:
    @staticmethod
    def get_user_progress(db: Session, user_id: int) -> List[Any]:
        return []

    @staticmethod
    def mark_problem_solved(db: Session, user_id: int, problem_id: str) -> bool:
        return True


class NotesService:
    @staticmethod
    def get_user_notes(db: Session, user_id: int) -> List[Any]:
        return []

    @staticmethod
    def save_note(db: Session, user_id: int, target_id: str, content: str) -> Dict[str, Any]:
        return {"user_id": user_id, "target_id": target_id, "content": content}


class XpService:
    @staticmethod
    def add_xp(db: Session, user: User, amount: int, action: str) -> User:
        from app.core.learning import log_xp
        log_xp(db, user, amount, action)
        db.commit()
        db.refresh(user)
        return user


class ActivityService:
    @staticmethod
    def log_daily_activity(db: Session, user_id: int, duration_secs: int) -> bool:
        from app.core.learning import update_activity
        update_activity(db, user_id, 0, 0, duration_secs)
        db.commit()
        return True


class StreakService:
    @staticmethod
    def calculate_streak(db: Session, user_id: int) -> Dict[str, int]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"current_streak": 0, "max_streak": 0}
        return {"current_streak": user.current_streak, "max_streak": user.max_streak}


class BookmarksService:
    @staticmethod
    def toggle_bookmark(db: Session, user_id: int, target_type: str, target_id: str) -> bool:
        return True


class SettingsService:
    @staticmethod
    def get_user_settings(db: Session, user_id: int) -> Dict[str, Any]:
        return {"theme": "dark", "notifications": True}

    @staticmethod
    def update_user_settings(db: Session, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        return settings
