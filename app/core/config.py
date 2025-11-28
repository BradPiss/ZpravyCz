import os
import secrets

class Settings:
    PROJECT_NAME: str = "Zpravodajský Portál"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./news.db"
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
