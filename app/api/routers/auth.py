from fastapi import APIRouter, Depends, Form, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import settings

router = APIRouter()
svc = AuthService()

@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...), next: str = Form(None), db: Session = Depends(get_db)):
    user = svc.authenticate(db, username, password)
    redirect = next if next else "/"
    if not user:
        return RedirectResponse(f"{redirect}?error=invalid_credentials" if "?" not in redirect else f"{redirect}&error=invalid_credentials", 302)
    
    token = create_access_token({"sub": str(user.id), "role": user.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    resp = RedirectResponse(redirect, 302)
    resp.set_cookie(key="access_token", value=token, httponly=True)
    return resp

@router.get("/logout")
async def logout(response: Response, next: str = None):
    resp = RedirectResponse(next if next else "/", 302)
    resp.delete_cookie("access_token")
    return resp

@router.post("/registrace")
async def register(email: str = Form(...), password: str = Form(...), name: str = Form(...), next: str = Form(None), db: Session = Depends(get_db)):
    user = svc.register(db, email, password, name)
    redirect = next if next else "/"
    if not user: return RedirectResponse(redirect, 302) # Email existuje
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    resp = RedirectResponse(redirect, 302)
    resp.set_cookie(key="access_token", value=token, httponly=True)
    return resp