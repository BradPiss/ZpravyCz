from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.models.enums import ArticleStatus
from app.api.dependencies import get_current_user
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Pomocná funkce pro načtení sidebar dat (abychom to nepsali 2x)
def get_common_data(db: Session):
    return {
        # Zde můžeme v budoucnu přidat třeba seznam kategorií pro menu
    }

@router.get("/")
async def home(
    request: Request, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    articles = db.query(Article)\
        .filter(Article.status == ArticleStatus.PUBLISHED)\
        .order_by(Article.created_at.desc())\
        .all()
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Zprávy.cz", "articles": articles, "user": user}
    )

@router.get("/clanek/{article_id}", name="article_detail")
async def article_detail(
    request: Request, 
    article_id: int, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    
    # Související články (ze stejné kategorie, pokud možno)
    related_query = db.query(Article).filter(
        Article.status == ArticleStatus.PUBLISHED, 
        Article.id != article_id
    )
    
    if article.category_id:
        # Zkusíme najít články ze stejné kategorie
        related_query = related_query.filter(Article.category_id == article.category_id)
    
    related_articles = related_query.limit(4).all()
    
    # Pokud je jich málo, doplníme náhodnými
    if len(related_articles) < 2:
        extra = db.query(Article).filter(
            Article.status == ArticleStatus.PUBLISHED, 
            Article.id != article_id
        ).limit(5).all()
        related_articles = list(set(related_articles + extra))[:2]

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

# NOVÝ ENDPOINT PRO KATEGORIE
@router.get("/kategorie/{category_id}", name="category_detail")
async def category_detail(
    request: Request, 
    category_id: int, 
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie nenalezena")

    # Načteme 10 nejnovějších článků z kategorie
    articles = db.query(Article)\
        .filter(Article.status == ArticleStatus.PUBLISHED, Article.category_id == category_id)\
        .order_by(Article.created_at.desc())\
        .limit(10)\
        .all()

    # ZMĚNA: Posíláme do "category.html"
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