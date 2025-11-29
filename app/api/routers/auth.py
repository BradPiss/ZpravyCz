from fastapi import APIRouter, Depends, Form, status, Response, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import Role
from app.core.security import verify_password, create_access_token, hash_password
from app.core.config import settings
from datetime import timedelta
from typing import Optional

router = APIRouter()

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(None), # Přijímáme parametr 'next' z formuláře
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == username).first()
    
    # Určení, kam přesměrovat (buď na 'next', nebo na HP)
    redirect_url = next if next else "/"

    if not user or not verify_password(password, user.password_hash):
        # Při chybě vrátíme tam, odkud přišel, ale s chybou
        error_url = f"{redirect_url}?error=invalid_credentials" if "?" not in redirect_url else f"{redirect_url}&error=invalid_credentials"
        return RedirectResponse(url=error_url, status_code=status.HTTP_302_FOUND)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Úspěch -> jdeme na původní stránku
    resp = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="access_token", value=access_token, httponly=True)
    return resp

@router.get("/logout")
async def logout(
    response: Response, 
    next: Optional[str] = Query(None) # Přijímáme 'next' z URL (?next=...)
):
    redirect_url = next if next else "/"
    resp = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("access_token")
    return resp

@router.post("/registrace")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    next: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    redirect_url = next if next else "/"

    if db.query(User).filter(User.email == email).first():
        # Pokud mail existuje, vrátíme se s chybou (zjednodušeno)
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    new_user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=Role.READER,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role}
    )
    
    resp = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="access_token", value=access_token, httponly=True)
    return resp