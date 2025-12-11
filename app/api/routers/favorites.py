from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.article_service import ArticleService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
service = ArticleService()

@router.post("/clanek/{article_id}/oblibit")
async def toggle_favorite(article_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user: return JSONResponse({"error": "login"}, 401)
    
    action = service.toggle_favorite(db, user, article_id)
    if not action: return JSONResponse({"error": "not_found"}, 404)
    
    return JSONResponse({"status": "success", "action": action})

@router.get("/oblibene")
async def list_favorites(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user: return RedirectResponse("/?error=login", 302)
    
    # SQLAlchemy relationship to načte samo, jen seřadíme
    saved = user.saved_articles_rel
    saved.sort(key=lambda x: x.created_at, reverse=True)

    return templates.TemplateResponse("favorites.html", {
        "request": request, "articles": saved, "user": user, "title": "Oblíbené"
    })