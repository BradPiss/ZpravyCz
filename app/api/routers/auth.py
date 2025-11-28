from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.enums import Role

router = APIRouter()


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login endpoint. Accepts form data (username=email, password).
    Creates JWT token, stores in cookie, redirects to homepage.
    """
    # Find user by email
    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        # Invalid credentials - redirect back to homepage
        return RedirectResponse(url="/", status_code=302)
    
    if not user.is_active:
        # Inactive user - redirect back to homepage
        return RedirectResponse(url="/", status_code=302)
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Redirect to homepage with cookie set
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax",
        secure=True
    )
    return response


@router.post("/registrace")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Registration endpoint. Accepts form data (name, email, password).
    Creates user with READER role, auto-login with JWT in cookie.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # Email already exists - redirect back to homepage
        return RedirectResponse(url="/", status_code=302)
    
    # Create new user
    new_user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        is_active=True,
        role=Role.READER
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login: create JWT token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    # Redirect to homepage with cookie set
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax",
        secure=True
    )
    return response


@router.get("/logout")
async def logout():
    """
    Logout endpoint. Deletes cookie and redirects to homepage.
    """
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response
