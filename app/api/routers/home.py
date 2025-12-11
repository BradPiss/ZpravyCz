from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.models.enums import ArticleStatus
from app.models.comment import Comment 
from app.models.tag import Tag
from fastapi.responses import RedirectResponse
from app.api.dependencies import get_current_user
from sqlalchemy import or_

import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Hlavní článek (Pozice 1)
    main_article = db.query(Article).filter(Article.home_position == 1, Article.status == ArticleStatus.PUBLISHED).first()
    
    # 2. Sekundární články (Pozice 2, 3, 4)
    secondary_db = db.query(Article).filter(
        Article.home_position.in_([2, 3, 4]), 
        Article.status == ArticleStatus.PUBLISHED
    ).all()
    
    # Namapujeme články na pozice
    pos_map = {a.home_position: a for a in secondary_db}
    
    # Vytvoříme seznam fixně o 3 prvcích. 
    # Pokud na pozici nic není, bude tam None. Tím zajistíme, že se mřížka neposune.
    # Index 0 = Pozice 2 (Vlevo), Index 1 = Pozice 3 (Střed), Index 2 = Pozice 4 (Vpravo)
    promoted_articles = [pos_map.get(i) for i in [2, 3, 4]]

    # 3. Zbytek (Seznam - Pozice 0)
    list_articles = db.query(Article)\
        .filter(
            Article.status == ArticleStatus.PUBLISHED,
            Article.home_position == 0
        )\
        .order_by(Article.created_at.desc())\
        .limit(50)\
        .all()

    # 4. Fallback pro hlavní článek (pokud chybí, vezmeme nejnovější promoted)
    if not main_article:
        # Zkusíme najít náhradu v historii
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

    # Pokud stále nemáme hlavní článek a máme něco v seznamu, vezmeme první ze seznamu
    if not main_article and list_articles:
        main_article = list_articles.pop(0)

    # Do šablony posíláme proměnné odděleně, ne v jednom balíku "articles"
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "title": "Zprávy.cz", 
            "main_article": main_article,
            "promoted_articles": promoted_articles, # Seznam 3 prvků (články nebo None)
            "list_articles": list_articles,
            "user": user
        }
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

@router.get("/hledat")
async def search_articles(
    request: Request,
    q: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not q:
        return RedirectResponse("/")

    # OPRAVA: Musíme použít .outerjoin(Article.tags)
    # Tím říkáme: "Připoj k článkům jejich tagy."
    articles = db.query(Article).outerjoin(Article.tags).filter(
        Article.status == ArticleStatus.PUBLISHED,
        or_(
            Article.title.contains(q),     # Hledá v nadpisu
            Article.perex.contains(q),     # Hledá v perexu
            Tag.name.contains(q)           # Hledá v názvu tagu
        )
    ).distinct().order_by(Article.created_at.desc()).all()
    # .distinct() je důležité, aby se článek neukázal 2x, pokud má víc shodných tagů

    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "title": f"Hledání: {q}",
        "query": q,
        "articles": articles,
        "user": user
    })