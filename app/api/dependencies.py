from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db # <--- ZMĚNA (bylo app.core.database)
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Přečte cookie 'access_token', ověří ho a vrátí objekt User.
    Pokud není přihlášen, vrátí None.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
        
    # Použijeme repozitář pro čistotu, nebo přímý dotaz (zde stačí přímý pro rychlost/závislost)
    # Ale abychom dodrželi architekturu, měli bychom použít repo, 
    # nicméně dependency injection repozitářů je složitější, 
    # takže zde je přímý dotaz přes SQLAlchemy v pořádku (nebo použití User modelu).
    # 1. Musíme vytvořit instanci repozitáře (závorky na konci)
    user_repo = UserRepository()
    
    # 2. Musíme user_id převést na int(), protože v tokenu je to string
    try:
        return user_repo.get_by_id(db, int(user_id))
    except (ValueError, TypeError):
        return None