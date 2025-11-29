from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

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
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user