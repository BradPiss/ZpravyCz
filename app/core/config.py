import os

class Settings:
    PROJECT_NAME: str = "Zpravodajský Portál"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./news.db"
    
    # NOVÉ: Nastavení pro bezpečnost
    SECRET_KEY: str = "tvoje-super-tajne-heslo-ktere-nikdo-neuhodne"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hodin

settings = Settings()