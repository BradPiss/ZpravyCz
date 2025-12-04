from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
from app.models.vote import Vote
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

# --- SPRÁVA UŽIVATELŮ (Jen pro Adminy) ---

@router.get("/uzivatele")
async def admin_user_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # OPRAVA: Nejdřív zjistíme, jestli je uživatel přihlášený (not user)
    if not user or user.role != Role.ADMIN:
        # Pokud není přihlášen nebo není admin -> přesměrovat na login nebo vyhodit chybu
        return RedirectResponse("/?error=unauthorized", status_code=302)
    
    users = db.query(User).order_by(User.id.desc()).all()
    
    return templates.TemplateResponse("admin/user_list.html", {
        "request": request,
        "users": users,
        "user": user,
        "title": "Správa uživatelů"
    })

@router.get("/uzivatele/{user_id}/upravit")
async def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # OPRAVA: Kontrola existence uživatele
    if not user or user.role != Role.ADMIN:
        return RedirectResponse("/?error=unauthorized", status_code=302)
        
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
        
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request,
        "edit_user": edit_user,
        "user": user,
        "title": f"Úprava uživatele: {edit_user.name}"
    })

@router.post("/uzivatele/{user_id}/upravit")
async def edit_user_submit(
    user_id: int,
    role: str = Form(...),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # OPRAVA: Kontrola existence uživatele
    if not user or user.role != Role.ADMIN:
        return RedirectResponse("/?error=unauthorized", status_code=302)
    
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    # Ochrana: Nemůžu sebrat admin práva sám sobě ani se zablokovat
    if edit_user.id == user.id:
        # Pokud edituju sám sebe, vynutíme, že zůstanu Admin a Aktivní
        edit_user.role = Role.ADMIN
        edit_user.is_active = True
    else:
        edit_user.role = role
        edit_user.is_active = is_active
        
    db.commit()
    
    return RedirectResponse("/admin/uzivatele", status_code=302)

@router.post("/uzivatele/{user_id}/smazat")
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # 1. Kontrola práv
    if not user or user.role != Role.ADMIN:
        return RedirectResponse("/?error=unauthorized", status_code=302)
        
    del_user = db.query(User).filter(User.id == user_id).first()
    
    # 2. Ochrana: Nemůžu smazat sám sebe
    if del_user and del_user.id != user.id:
        
        # A) Články: Převedeme na Admina (zachráníme obsah)
        user_articles = db.query(Article).filter(Article.author_id == del_user.id).all()
        for article in user_articles:
            article.author_id = user.id
            
        # B) Komentáře: SMAŽEME JE (Změna oproti minule)
        # Díky kaskádě v modelu se smažou i lajky u těchto komentářů a odpovědi na ně
        user_comments = db.query(Comment).filter(Comment.author_id == del_user.id).all()
        for comment in user_comments:
            db.delete(comment)
            
        # --- C) HLASY (TADY JE OPRAVA) ---
        # 1. Zjistíme, u kterých komentářů uživatel hlasoval
        votes_to_delete = db.query(Vote).filter(Vote.user_id == del_user.id).all()
        affected_comment_ids = {v.comment_id for v in votes_to_delete} # Množina unikátních ID
        
        # 2. Smažeme hlasy
        for v in votes_to_delete:
            db.delete(v)
        
        db.commit() # Uložíme smazání, aby .count() níže viděl nový stav
        
        # 3. Přepočítáme čísla u dotčených komentářů (Refresh Counters)
        for cid in affected_comment_ids:
            comment = db.query(Comment).filter(Comment.id == cid).first()
            if comment:
                comment.likes = db.query(Vote).filter(Vote.comment_id == cid, Vote.vote_type == "up").count()
                comment.dislikes = db.query(Vote).filter(Vote.comment_id == cid, Vote.vote_type == "down").count()
        
        # 3. Smazání uživatele
        db.delete(del_user)
        db.commit()
        
    return RedirectResponse("/admin/uzivatele", status_code=302)