import os
class Settings:
    PROJECT_NAME: str = "Zpravodajský Portál"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./news.db"

settings = Settings()
