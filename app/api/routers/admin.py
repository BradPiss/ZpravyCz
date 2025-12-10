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
from app.models.comment import Comment
from app.models.vote import Vote
from app.models.tag import Tag

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def check_permissions(user: User):
    if not user or user.role not in [Role.ADMIN, Role.EDITOR, Role.CHIEF_EDITOR]:
        raise HTTPException(status_code=403, detail="Nemáte oprávnění vstoupit do administrace.")

# Helper funkce pro zpracování tagů (vlož ji někam nad routery, nebo přímo do souboru)
def process_tags(db: Session, tags_str: str):
    if not tags_str:
        return []
    
    # Rozdělit podle čárky a očistit mezery
    tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
    # Odstranit duplicity v rámci vstupu
    tag_names = list(set(tag_names))
    
    final_tags = []
    for name in tag_names:
        # Zkusíme najít existující tag
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            # Pokud neexistuje, vytvoříme nový
            tag = Tag(name=name)
            db.add(tag)
            # Musíme flushnout, aby měl tag ID, pokud bychom ho hned potřebovali, 
            # ale SQLAlchemy si to pořeší při commitu
        final_tags.append(tag)
    return final_tags


# 1. SEZNAM
@router.get("/clanky")
async def admin_article_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    articles = db.query(Article).order_by(Article.created_at.desc()).all()
    return templates.TemplateResponse("admin/article_list.html", {"request": request, "articles": articles, "user": user, "title": "Správa článků"})

# 2. NOVÝ ČLÁNEK
@router.get("/clanky/novy")
async def create_article_form(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    categories = db.query(Category).all()
    return templates.TemplateResponse("admin/article_form.html", {"request": request, "categories": categories, "user": user, "article": None, "title": "Nový článek"})

# 3. ULOŽENÍ NOVÉHO
@router.post("/clanky/novy")
async def create_article_submit(
    title: str = Form(...),
    perex: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(...),
    tags: str = Form(""), # <--- PŘIJÍMÁME TAGY
    image_url: Optional[str] = Form(None),
    image_caption: Optional[str] = Form(None),
    status: str = Form(...),
    home_position: int = Form(0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    check_permissions(user)
    
    if status == ArticleStatus.PUBLISHED.value and user.role == Role.EDITOR:
        raise HTTPException(status_code=403, detail="Redaktor nemůže publikovat články.")

    if home_position > 0 and status == ArticleStatus.PUBLISHED.value:
        old_tenant = db.query(Article).filter(Article.home_position == home_position, Article.status == ArticleStatus.PUBLISHED).first()
        if old_tenant:
            old_tenant.home_position = 0
            db.add(old_tenant)
            
    if status != ArticleStatus.PUBLISHED.value:
        home_position = 0

    last_promoted = datetime.now(timezone.utc) if home_position == 1 else None

    new_article = Article(
        title=title, perex=perex, content=content, category_id=category_id, 
        image_url=image_url if image_url else None,
        image_caption=image_caption if image_caption else None, # <--- NOVÉ
        status=status, home_position=home_position, last_promoted_at=last_promoted,
        author_id=user.id, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    new_article.tags = process_tags(db, tags)
    db.add(new_article)
    db.commit()
    return RedirectResponse("/admin/clanky", status_code=302)

# 4. EDITACE
@router.get("/clanky/{article_id}/upravit")
async def edit_article_form(article_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article: raise HTTPException(404, "Článek nenalezen")
    categories = db.query(Category).all()
    return templates.TemplateResponse("admin/article_form.html", {"request": request, "categories": categories, "user": user, "article": article, "title": f"Úprava: {article.title}"})

# 5. ULOŽENÍ ZMĚN
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
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article: raise HTTPException(404, "Článek nenalezen")
    
    if status == ArticleStatus.PUBLISHED.value:
        if user.role == Role.EDITOR and article.status != ArticleStatus.PUBLISHED:
             raise HTTPException(status_code=403, detail="Redaktor nemůže publikovat koncepty.")

    if home_position > 0 and status == ArticleStatus.PUBLISHED.value:
        old_tenant = db.query(Article).filter(Article.home_position == home_position, Article.status == ArticleStatus.PUBLISHED).first()
        if old_tenant and old_tenant.id != article.id:
            old_tenant.home_position = 0
            db.add(old_tenant)
            
    if status != ArticleStatus.PUBLISHED.value:
        home_position = 0
        
    if home_position == 1 and article.home_position != 1:
        article.last_promoted_at = datetime.now(timezone.utc)
    
    article.title = title
    article.perex = perex
    article.content = content
    article.category_id = category_id
    article.image_url = image_url
    article.image_caption = image_caption # <--- NOVÉ
    article.status = status
    article.home_position = home_position
    article.updated_at = datetime.now(timezone.utc)
    article.tags = process_tags(db, tags)
    
    db.commit()
    return RedirectResponse("/admin/clanky", status_code=302)

# ... (zbytek souboru - mazání, uživatelé - zůstává stejný) ...
@router.post("/clanky/{article_id}/smazat")
async def delete_article(article_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_permissions(user)
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        comments = db.query(Comment).filter(Comment.article_id == article.id).all()
        for c in comments:
            db.query(Vote).filter(Vote.comment_id == c.id).delete()
            db.delete(c)
        db.delete(article)
        db.commit()
    return RedirectResponse("/admin/clanky", status_code=302)

@router.get("/uzivatele")
async def admin_user_list(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user or user.role != Role.ADMIN: return RedirectResponse("/?error=unauthorized", status_code=302)
    users = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse("admin/user_list.html", {"request": request, "users": users, "user": user, "title": "Správa uživatelů"})

@router.get("/uzivatele/{user_id}/upravit")
async def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user or user.role != Role.ADMIN: return RedirectResponse("/?error=unauthorized", status_code=302)
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user: raise HTTPException(404, "Nenalezen")
    return templates.TemplateResponse("admin/user_form.html", {"request": request, "edit_user": edit_user, "user": user, "title": f"Úprava: {edit_user.name}"})

@router.post("/uzivatele/{user_id}/upravit")
async def edit_user_submit(user_id: int, role: str = Form(...), is_active: bool = Form(False), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user or user.role != Role.ADMIN: return RedirectResponse("/?error=unauthorized", status_code=302)
    edit_user = db.query(User).filter(User.id == user_id).first()
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
    if not user or user.role != Role.ADMIN: return RedirectResponse("/?error=unauthorized", status_code=302)
    del_user = db.query(User).filter(User.id == user_id).first()
    if del_user and del_user.id != user.id:
        user_articles = db.query(Article).filter(Article.author_id == del_user.id).all()
        for a in user_articles: a.author_id = user.id
        user_comments = db.query(Comment).filter(Comment.author_id == del_user.id).all()
        for c in user_comments: db.delete(c)
        db.query(Vote).filter(Vote.user_id == del_user.id).delete()
        db.delete(del_user)
        db.commit()
    return RedirectResponse("/admin/uzivatele", status_code=302)