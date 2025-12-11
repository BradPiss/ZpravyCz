from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.models.db import get_db
from app.api.dependencies import get_current_user
from app.services.article_service import ArticleService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
svc = ArticleService()

@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    data = svc.get_homepage_data(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Zprávy.cz", "user": user, **data})

@router.get("/clanek/{article_id}", name="article_detail")
async def article_detail(request: Request, article_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    data = svc.get_detail(db, article_id)
    if not data: raise HTTPException(404, "Článek nenalezen")
    return templates.TemplateResponse("article_detail.html", {"request": request, "title": data['article'].title, "user": user, **data})

@router.get("/kategorie/{category_id}", name="category_detail")
async def category_detail(request: Request, category_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    cat = svc.category_repo.get_by_id(db, category_id)
    if not cat: raise HTTPException(404, "Kategorie nenalezena")
    # Lazy loading articles
    articles = [a for a in cat.articles if a.status.value == 'published']
    articles.sort(key=lambda x: x.created_at, reverse=True)
    return templates.TemplateResponse("category.html", {"request": request, "title": f"{cat.name} | Zprávy.cz", "articles": articles, "category": cat, "user": user})

@router.get("/hledat")
async def search(request: Request, q: str = "", db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not q: return RedirectResponse("/")
    articles = svc.search(db, q)
    return templates.TemplateResponse("search_results.html", {"request": request, "title": f"Hledání: {q}", "query": q, "articles": articles, "user": user})