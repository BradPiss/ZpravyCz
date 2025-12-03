from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.models.enums import ArticleStatus
from app.api.dependencies import get_current_user # Import dependency
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user) # Získat uživatele z cookie
):
    articles = db.query(Article)\
        .filter(Article.status == ArticleStatus.PUBLISHED)\
        .order_by(Article.created_at.desc())\
        .all()
    
    # Posíláme 'user' do šablony
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Zprávy.cz", "articles": articles, "user": user}
    )

@router.get("/clanek/{article_id}", name="article_detail")
async def article_detail(
    request: Request, 
    article_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    
    related_query = db.query(Article).filter(
        Article.status == ArticleStatus.PUBLISHED, 
        Article.id != article_id
    )
    if article.category_id:
        related_query = related_query.filter(Article.category_id == article.category_id)
    
    related_articles = related_query.limit(4).all()
    
    return templates.TemplateResponse(
        "article_detail.html", 
        {
            "request": request, 
            "title": article.title, 
            "article": article,
            "related_articles": related_articles,
            "user": user
        }
    )

@router.get("/kategorie/{category_id}", name="category_detail")
async def category_detail(
    request: Request, 
    category_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie nenalezena")

    articles = db.query(Article)\
        .filter(Article.status == ArticleStatus.PUBLISHED, Article.category_id == category_id)\
        .order_by(Article.created_at.desc())\
        .limit(50)\
        .all()

    return templates.TemplateResponse(
        "category.html", 
        {
            "request": request, 
            "title": f"{category.name} | Zprávy.cz", 
            "articles": articles,
            "category": category,
            "user": user
        }
    )

# ... (importy Comment) ...

@router.get("/clanek/{article_id}", name="article_detail")
async def article_detail(
    request: Request, 
    article_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    
    # ZMĚNA: Načteme jen POČET komentářů (count), ne seznam
    comments_count = db.query(Comment)\
        .filter(Comment.article_id == article_id, Comment.is_visible == True)\
        .count()

    related_query = db.query(Article).filter(
        Article.status == ArticleStatus.PUBLISHED, 
        Article.id != article_id
    )
    if article.category_id:
        related_query = related_query.filter(Article.category_id == article.category_id)
    
    related_articles = related_query.limit(4).all()
    
    return templates.TemplateResponse(
        "article_detail.html", 
        {
            "request": request, 
            "title": article.title, 
            "article": article,
            "comments_count": comments_count, # Posíláme jen číslo
            "related_articles": related_articles,
            "user": user
        }
    )