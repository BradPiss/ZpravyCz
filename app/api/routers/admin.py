from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.models.db import get_db
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.models.vote import Vote
from app.models.enums import Role, ArticleStatus
from app.api.dependencies import get_current_user
from app.services.article_service import ArticleService
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Inicializace služeb a repozitářů
article_service = ArticleService()
cat_repo = CategoryRepository()
user_repo = UserRepository()

def check_permissions(user: User):
    """Ověří, zda má uživatel právo vstoupit do administrace."""
    if not user or user.role not in [Role.ADMIN, Role.EDITOR, Role.CHIEF_EDITOR]:
        raise HTTPException(status_code=403, detail="Nemáte oprávnění vstoupit do administrace.")

def check_admin_permissions(user: User):
    """Ověří, zda je uživatel Administrátor (pro správu uživatelů)."""
    if not user or user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Tuto akci může provést pouze administrátor.")

# --- SPRÁVA ČLÁNKŮ ---

@router.get("/clanky")
async def admin_article_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    articles = article_service.repo.get_all_admin(db)
    return templates.TemplateResponse("admin/article_list.html", {"request": request, "articles": articles, "user": user})

@router.get("/clanky/novy")
async def create_article_form(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    categories = cat_repo.get_all(db)
    return templates.TemplateResponse("admin/article_form.html", {
        "request": request, 
        "categories": categories, 
        "user": user, 
        "article": None, 
        "title": "Nový článek"
    })

@router.post("/clanky/novy")
async def create_article_submit(
    title: str = Form(...),
    perex: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    tags: str = Form(""),
    image_url: Optional[str] = Form(None),
    image_caption: Optional[str] = Form(None),
    status: str = Form(...),
    home_position: int = Form(0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    check_permissions(user)
    
    # Redaktor nemůže publikovat rovnou
    if status == ArticleStatus.PUBLISHED.value and user.role == Role.EDITOR:
        raise HTTPException(status_code=403, detail="Redaktor nemůže publikovat články.")

    # Zabalíme data a vyčistíme systémové proměnné pomocí .pop()
    data = locals()
    data.pop('db', None)
    data.pop('user', None)
    
    article_service.create_article(db, data, user.id)
    return RedirectResponse("/admin/clanky", status_code=302)

@router.get("/clanky/{article_id}/upravit")
async def edit_article_form(article_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    article = article_service.repo.get_by_id(db, article_id)
    if not article: 
        raise HTTPException(404, "Článek nenalezen")
    
    categories = cat_repo.get_all(db)
    return templates.TemplateResponse("admin/article_form.html", {
        "request": request, 
        "categories": categories, 
        "user": user, 
        "article": article, 
        "title": article.title
    })

@router.post("/clanky/{article_id}/upravit")
async def edit_article_submit(
    article_id: int,
    title: str = Form(...),
    perex: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    tags: str = Form(""),
    image_url: Optional[str] = Form(None),
    image_caption: Optional[str] = Form(None),
    status: str = Form(...),
    home_position: int = Form(0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    check_permissions(user)
    
    article = article_service.repo.get_by_id(db, article_id)
    if not article: raise HTTPException(404)

    # Kontrola oprávnění pro editora
    if status == ArticleStatus.PUBLISHED.value:
        if user.role == Role.EDITOR and article.status != ArticleStatus.PUBLISHED:
             raise HTTPException(status_code=403, detail="Redaktor nemůže publikovat koncepty.")

    data = locals()
    data.pop('db', None)
    data.pop('user', None)
    data.pop('article_id', None)
    data.pop('article', None)
    
    article_service.update_article(db, article_id, data)
    return RedirectResponse("/admin/clanky", status_code=302)

@router.post("/clanky/{article_id}/smazat")
async def delete_article(article_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    article_service.delete_article(db, article_id)
    return RedirectResponse("/admin/clanky", status_code=302)


# --- SPRÁVA UŽIVATELŮ ---

@router.get("/uzivatele")
async def admin_user_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Pokud není admin, přesměrujeme pryč
    if not user or user.role != Role.ADMIN: 
        return RedirectResponse("/", status_code=302)
        
    users = user_repo.get_all(db)
    return templates.TemplateResponse("admin/user_list.html", {"request": request, "users": users, "user": user})

@router.get("/uzivatele/{user_id}/upravit")
async def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_admin_permissions(user)
    
    edit_user = user_repo.get_by_id(db, user_id)
    if not edit_user: 
        raise HTTPException(404, "Uživatel nenalezen")
        
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request, 
        "edit_user": edit_user, 
        "user": user, 
        "title": f"Úprava: {edit_user.name}"
    })

@router.post("/uzivatele/{user_id}/upravit")
async def edit_user_submit(
    user_id: int, 
    role: str = Form(...), 
    is_active: bool = Form(False), 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    check_admin_permissions(user)
    
    edit_user = user_repo.get_by_id(db, user_id)
    if not edit_user:
        raise HTTPException(404, "Uživatel nenalezen")

    # Ochrana: Admin si nemůže sám sobě sebrat práva nebo se deaktivovat
    if edit_user.id == user.id:
        edit_user.role = Role.ADMIN
        edit_user.is_active = True
    else:
        edit_user.role = role
        edit_user.is_active = is_active
        
    db.commit()
    return RedirectResponse("/admin/uzivatele", status_code=302)

@router.post("/uzivatele/{user_id}/smazat")
async def delete_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_admin_permissions(user)
    
    del_user = user_repo.get_by_id(db, user_id)
    
    # Ochrana: Nemůžu smazat sám sebe
    if del_user and del_user.id != user.id:
        
        # 1. Převedeme články smazaného uživatele na aktuálního admina (aby nezmizel obsah)
        user_articles = db.query(Article).filter(Article.author_id == del_user.id).all()
        for a in user_articles: 
            a.author_id = user.id
            
        # 2. Smažeme jeho komentáře
        user_comments = db.query(Comment).filter(Comment.author_id == del_user.id).all()
        for c in user_comments: 
            db.delete(c)
            
        # 3. Smažeme jeho hlasy
        db.query(Vote).filter(Vote.user_id == del_user.id).delete()
        
        # 4. Smažeme uživatele
        user_repo.delete(db, del_user)
        
    return RedirectResponse("/admin/uzivatele", status_code=302)