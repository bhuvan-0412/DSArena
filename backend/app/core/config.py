from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DSArena API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./dsarena.db"  # Fallback to local SQLite for easy MVP dev, override with Postgres in prod
    
    # Auth
    CLERK_SECRET_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""

    model_config = ConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
