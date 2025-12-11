import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Zpravodajský Portál"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./news.db"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-tajne-heslo-pro-vyvoj")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

settings = Settings()