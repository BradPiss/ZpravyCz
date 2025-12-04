from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.models.enums import ArticleStatus
from app.models.comment import Comment # <--- DŮLEŽITÉ: Import Comment
from app.api.dependencies import get_current_user
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Načteme články na pevných pozicích
    main_article = db.query(Article).filter(Article.home_position == 1, Article.status == ArticleStatus.PUBLISHED).first()
    
    secondary_db = db.query(Article).filter(
        Article.home_position.in_([2, 3, 4]), 
        Article.status == ArticleStatus.PUBLISHED
    ).all()
    
    pos_map = {a.home_position: a for a in secondary_db}
    secondary_articles = [pos_map.get(i) for i in [2, 3, 4] if pos_map.get(i)]

    # 2. Zbytek (Seznam)
    list_articles = db.query(Article)\
        .filter(
            Article.status == ArticleStatus.PUBLISHED,
            Article.home_position == 0
        )\
        .order_by(Article.created_at.desc())\
        .limit(50)\
        .all()

    # 3. Fallback
    if not main_article:
        history_fallback = db.query(Article)\
            .filter(
                Article.status == ArticleStatus.PUBLISHED,
                Article.last_promoted_at != None,
                Article.home_position == 0 
            )\
            .order_by(Article.last_promoted_at.desc())\
            .first()
        if history_fallback:
            main_article = history_fallback

    # Pokud stále nic, vezmeme první ze seznamu
    exclude_ids = [a.id for a in secondary_articles if a]
    if main_article:
        exclude_ids.append(main_article.id)

    # Znovu načteme seznam bez vyloučených (aby se neopakovaly)
    list_articles = db.query(Article)\
        .filter(
            Article.status == ArticleStatus.PUBLISHED,
            Article.home_position == 0,
            Article.id.notin_(exclude_ids)
        )\
        .order_by(Article.created_at.desc())\
        .limit(50)\
        .all()

    if not main_article and list_articles:
        main_article = list_articles.pop(0)

    all_articles = []
    if main_article: all_articles.append(main_article)
    all_articles.extend(secondary_articles)
    all_articles.extend(list_articles)

    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Zprávy.cz", "articles": all_articles, "user": user}
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
    
    # --- TADY JE TA OPRAVA ---
    # Spočítáme komentáře
    count = db.query(Comment)\
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
            "comments_count": count, # Pro tlačítko
            "total_count": count,    # Pro nadpis "Diskuse (X)" - TOTO JSI CHTĚL
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