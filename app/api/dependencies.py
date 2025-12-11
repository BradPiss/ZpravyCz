from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.enums import Role

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """
    Vrátí přihlášeného uživatele nebo None.
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
        
    user_repo = UserRepository()
    try:
        return user_repo.get_by_id(db, int(user_id))
    except (ValueError, TypeError):
        return None

# NOVÉ: Centralizovaná kontrola oprávnění
def get_current_admin_editor(user: User = Depends(get_current_user)) -> User:
    """
    Ověří, zda je uživatel přihlášen a má práva vstoupit do administrace.
    Pokud ne, vyhodí 403 (kterou pak router odchytí nebo vyřeší).
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nepřihlášen")
    
    if user.role not in [Role.ADMIN, Role.EDITOR, Role.CHIEF_EDITOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nemáte oprávnění.")
    
    return user

def get_current_super_admin(user: User = Depends(get_current_user)) -> User:
    """Pouze pro hlavního admina (správa uživatelů)."""
    if not user or user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pouze pro administrátory.")
    return user