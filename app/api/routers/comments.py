from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.api.dependencies import get_current_user
from app.services.article_service import ArticleService
from app.services.comment_service import CommentService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
svc = CommentService()
art_svc = ArticleService()

@router.get("/clanek/{article_id}/diskuse")
async def show_comments(request: Request, article_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    article = art_svc.get_by_id(db, article_id)
    
    if not article: 
        raise HTTPException(404, "Článek nenalezen")
    
    comments = svc.get_tree(db, article_id, user.id if user else None)
    return templates.TemplateResponse("comments.html", {"request": request, "article": article, "comments": comments, "user": user})

@router.post("/clanek/{article_id}/komentar")
async def add_comment(article_id: int, content: str = Form(...), parent_id: int = Form(None), db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user or not user.is_active: 
        return RedirectResponse(f"/clanek/{article_id}/diskuse?error=login", 302)
    
    svc.add(db, content, article_id, user.id, parent_id)
    return RedirectResponse(f"/clanek/{article_id}/diskuse", 302)

@router.post("/komentar/{comment_id}/vote")
async def vote(comment_id: int, vote_type: str = Form(...), db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: 
        return JSONResponse({"error": "login"}, 401)
    
    res = svc.vote(db, comment_id, user.id, vote_type)
    return JSONResponse(res) if res else JSONResponse({"error": "not found"}, 404)

@router.post("/komentar/{comment_id}/smazat")
async def delete(comment_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    aid = svc.delete_comment(db, comment_id, user)
    return RedirectResponse(f"/clanek/{aid}/diskuse", 302) if aid else RedirectResponse("/", 302)