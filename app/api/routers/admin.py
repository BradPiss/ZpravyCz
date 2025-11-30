from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.models.enums import ArticleStatus, Role
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Pomocná funkce pro kontrolu práv
def check_permissions(user: User):
    if not user or user.role not in [Role.ADMIN, Role.EDITOR]:
        raise HTTPException(status_code=403, detail="Nemáte oprávnění vstoupit do administrace.")

# 1. SEZNAM ČLÁNKŮ
@router.get("/clanky")
async def admin_article_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    
    # Načteme všechny články seřazené od nejnovějšího
    articles = db.query(Article).order_by(Article.created_at.desc()).all()
    
    return templates.TemplateResponse("admin/article_list.html", {
        "request": request,
        "articles": articles,
        "user": user,
        "title": "Správa článků"
    })

# 2. NOVÝ ČLÁNEK (Formulář)
@router.get("/clanky/novy")
async def create_article_form(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    categories = db.query(Category).all()
    
    return templates.TemplateResponse("admin/article_form.html", {
        "request": request,
        "categories": categories,
        "user": user,
        "article": None, # Žádný článek = nový článek
        "title": "Nový článek"
    })

# 3. ULOŽENÍ NOVÉHO ČLÁNKU
@router.post("/clanky/novy")
async def create_article_submit(
    title: str = Form(...),
    perex: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    image_url: Optional[str] = Form(None),
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    check_permissions(user)
    
    new_article = Article(
        title=title,
        perex=perex,
        content=content,
        category_id=category_id,
        image_url=image_url if image_url else None,
        status=status,
        author_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(new_article)
    db.commit()
    return RedirectResponse("/admin/clanky", status_code=302)

# 4. EDITACE (Formulář)
@router.get("/clanky/{article_id}/upravit")
async def edit_article_form(article_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    
    article = db.query(Article).filter(Article.id == article_id).first()
    categories = db.query(Category).all()
    
    if not article:
        raise HTTPException(404, "Článek nenalezen")

    return templates.TemplateResponse("admin/article_form.html", {
        "request": request,
        "categories": categories,
        "user": user,
        "article": article, # Předvyplnění formuláře
        "title": f"Úprava: {article.title}"
    })

# 5. ULOŽENÍ ZMĚN
@router.post("/clanky/{article_id}/upravit")
async def edit_article_submit(
    article_id: int,
    title: str = Form(...),
    perex: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    image_url: Optional[str] = Form(None),
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    check_permissions(user)
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(404, "Článek nenalezen")
    
    # Aktualizace polí
    article.title = title
    article.perex = perex
    article.content = content
    article.category_id = category_id
    article.image_url = image_url
    article.status = status
    article.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    return RedirectResponse("/admin/clanky", status_code=302)

# 6. SMAZÁNÍ
@router.post("/clanky/{article_id}/smazat")
async def delete_article(article_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        
    return RedirectResponse("/admin/clanky", status_code=302)