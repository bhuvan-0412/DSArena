from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "dsarena.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "DSArena API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DB_PATH.as_posix()}"
    
    # Auth
    CLERK_SECRET_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""

    model_config = ConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
