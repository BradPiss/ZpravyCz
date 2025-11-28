from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Read JWT token from 'access_token' cookie.
    Returns User object if valid, None otherwise.
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
    
    try:
        user_id_int = int(user_id)
    except ValueError:
        return None
    
    user = db.query(User).filter(User.id == user_id_int).first()
    return user
