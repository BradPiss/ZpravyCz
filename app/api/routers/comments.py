from fastapi import APIRouter, Depends, Form, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.article import Article
from app.models.vote import Vote
from app.models.enums import Role
from app.api.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ZOBRAZENÍ DISKUSE
@router.get("/clanek/{article_id}/diskuse")
async def show_comments(
    request: Request,
    article_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Článek nenalezen")
    
    # 1. Načíst všechny komentáře
    all_comments = db.query(Comment)\
        .filter(Comment.article_id == article_id, Comment.is_visible == True)\
        .order_by(Comment.created_at.asc())\
        .all()
    
    # 2. Zjistit hlasy uživatele
    user_votes_map = {}
    if user:
        votes = db.query(Vote).filter(Vote.user_id == user.id).all()
        for v in votes:
            user_votes_map[v.comment_id] = v.vote_type

    # 3. Příprava stromu
    replies_map = {} 
    
    for c in all_comments:
        # Zjištění hlasu
        vote = user_votes_map.get(c.id, None)
        
        # --- TOTO PŘIDEJ (Sanitární kontrola) ---
        # Pokud je počet lajků 0, nesmí svítit ikonka (opravuje vizuální chyby)
        if vote == 'up' and c.likes == 0: vote = None
        if vote == 'down' and c.dislikes == 0: vote = None
        # ----------------------------------------
        
        c.user_vote = vote
        
        # Inicializace dětí
        c.children = []
        if c.parent_id:
            if c.parent_id not in replies_map:
                replies_map[c.parent_id] = []
            replies_map[c.parent_id].insert(0, c)

    for c in all_comments:
        c.children = replies_map.get(c.id, [])

    root_comments = [c for c in all_comments if c.parent_id is None]
    root_comments.sort(key=lambda x: x.created_at, reverse=True)

    return templates.TemplateResponse("comments.html", {
        "request": request,
        "article": article,
        "comments": root_comments, 
        "user": user
    })

# PŘIDÁNÍ KOMENTÁŘE
@router.post("/clanek/{article_id}/komentar")
async def add_comment(
    article_id: int,
    content: str = Form(...),
    parent_id: int = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(f"/clanek/{article_id}/diskuse?error=login_required", status_code=302)
    if not user.is_active:
        return RedirectResponse(f"/clanek/{article_id}/diskuse?error=user_blocked", status_code=302)

    new_comment = Comment(
        content=content,
        article_id=article_id,
        author_id=user.id,
        parent_id=parent_id,
        created_at=datetime.now(timezone.utc),
        is_visible=True,
        likes=0,
        dislikes=0
    )
    db.add(new_comment)
    db.commit()
    
    return RedirectResponse(f"/clanek/{article_id}/diskuse", status_code=302)

# HLASOVÁNÍ (OPRAVA: Počítání řádků pro 100% jistotu)
@router.post("/komentar/{comment_id}/vote")
async def vote_comment(
    comment_id: int,
    vote_type: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return JSONResponse({"error": "login_required"}, status_code=401)

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return JSONResponse({"error": "not_found"}, status_code=404)

    # 1. Změna hlasu v tabulce Votes
    existing_vote = db.query(Vote).filter(Vote.user_id == user.id, Vote.comment_id == comment_id).first()
    current_user_vote = "none"

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.delete(existing_vote) # Toggle off
            current_user_vote = "none"
        else:
            existing_vote.vote_type = vote_type # Změna
            current_user_vote = vote_type
    else:
        new_vote = Vote(user_id=user.id, comment_id=comment_id, vote_type=vote_type)
        db.add(new_vote)
        current_user_vote = vote_type

    db.commit() # Uložíme změnu hlasu

    # 2. PŘEPOČÍTÁNÍ (The "Bulletproof" Fix)
    # Spočítáme skutečný počet řádků v DB. Tohle se nikdy nesplete.
    real_up_votes = db.query(Vote).filter(Vote.comment_id == comment_id, Vote.vote_type == "up").count()
    real_down_votes = db.query(Vote).filter(Vote.comment_id == comment_id, Vote.vote_type == "down").count()

    # Uložíme správná čísla do komentáře (pro příští načtení)
    comment.likes = real_up_votes
    comment.dislikes = real_down_votes
    db.commit()
    
    return JSONResponse({
        "likes": real_up_votes,
        "dislikes": real_down_votes,
        "user_vote": current_user_vote
    })

# SMAZÁNÍ KOMENTÁŘE
@router.post("/komentar/{comment_id}/smazat")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        is_admin = user and user.role == Role.ADMIN
        is_author = user and user.id == comment.author_id
        if is_admin or is_author:
            # Smažeme i všechny hlasy k tomuto komentáři, aby nezůstal bordel
            db.query(Vote).filter(Vote.comment_id == comment.id).delete()
            db.delete(comment)
            db.commit()
            
    return RedirectResponse(f"/clanek/{comment.article_id}/diskuse", status_code=302)