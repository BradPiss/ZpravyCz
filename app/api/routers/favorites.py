from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.article import Article
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 1. PŘEPÍNAČ (TOGGLE) OBLÍBENÉHO - AJAX
@router.post("/clanek/{article_id}/oblibit")
async def toggle_favorite(
    article_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return JSONResponse({"error": "login_required"}, status_code=401)

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return JSONResponse({"error": "not_found"}, status_code=404)

    # Zjistíme, jestli už je v oblíbených
    is_saved = article in user.saved_articles_rel
    
    if is_saved:
        user.saved_articles_rel.remove(article) # Odstranit
        action = "removed"
    else:
        user.saved_articles_rel.append(article) # Přidat
        action = "added"
        
    db.commit()
    
    return JSONResponse({"status": "success", "action": action})

# 2. SEZNAM OBLÍBENÝCH ČLÁNKŮ
@router.get("/oblibene")
async def list_favorites(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/?error=login_required", status_code=302)
    
    # Načteme uživatelovy oblíbené články
    # (SQLAlchemy to načte automaticky přes relationship, ale můžeme to seřadit)
    saved_articles = user.saved_articles_rel
    
    # Seřadíme v Pythonu od nejnovějšího (pokud chceme)
    saved_articles.sort(key=lambda x: x.created_at, reverse=True)

    return templates.TemplateResponse("favorites.html", {
        "request": request,
        "articles": saved_articles,
        "user": user,
        "title": "Oblíbené články"
    })