from fastapi import APIRouter, Depends, Form, status, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.article import Article
from app.models.enums import Role
from app.api.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ZOBRAZENÍ DISKUSE (S logikou stromu)
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
    
    # Načteme všechny viditelné komentáře
    all_comments = db.query(Comment)\
        .filter(Comment.article_id == article_id, Comment.is_visible == True)\
        .order_by(Comment.created_at.desc())\
        .all()
        
    # Python logika: Sestavení stromu (pouze 2 úrovně: Rodič -> Děti)
    root_comments = []
    replies_map = {} # id_rodice -> [seznam_deti]

    # Rozdělení na rodiče a děti
    for c in all_comments:
        if c.parent_id is None:
            root_comments.append(c)
        else:
            if c.parent_id not in replies_map:
                replies_map[c.parent_id] = []
            replies_map[c.parent_id].insert(0, c) # Nejnovější odpovědi nahoru

    # Připojíme děti k rodičům (dočasně pro šablonu)
    for c in root_comments:
        c.children = replies_map.get(c.id, [])

    return templates.TemplateResponse("comments.html", {
        "request": request,
        "article": article,
        "comments": root_comments, # Posíláme jen kořenové, děti jsou uvnitř nich
        "user": user
    })

# PŘIDÁNÍ KOMENTÁŘE (I ODPOVĚDI)
@router.post("/clanek/{article_id}/komentar")
async def add_comment(
    article_id: int,
    content: str = Form(...),
    parent_id: int = Form(None), # Může být None (nové vlákno) nebo ID (odpověď)
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
        is_visible=True
    )
    db.add(new_comment)
    db.commit()
    
    return RedirectResponse(f"/clanek/{article_id}/diskuse", status_code=302)

# HLASOVÁNÍ (Like/Dislike)
@router.post("/komentar/{comment_id}/vote")
async def vote_comment(
    comment_id: int,
    vote_type: str = Form(...), # "up" nebo "down"
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if vote_type == "up":
            comment.likes += 1
        elif vote_type == "down":
            comment.dislikes += 1
        db.commit()
    
    # Vrátíme se zpět na diskusi o článku
    back_url = f"/clanek/{comment.article_id}/diskuse" if comment else "/"
    return RedirectResponse(back_url, status_code=302)

# SMAZÁNÍ KOMENTÁŘE
@router.post("/komentar/{comment_id}/smazat")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(404, "Komentář nenalezen")
        
    # Kontrola práv: Smazat může ADMIN nebo AUTOR komentáře
    is_admin = user and user.role == Role.ADMIN
    is_author = user and user.id == comment.author_id
    
    if is_admin or is_author:
        # Fyzicky nesmažeme, jen skryjeme (soft delete) nebo smažeme úplně
        # Tady smažeme úplně pro jednoduchost
        db.delete(comment)
        db.commit()
    
    return RedirectResponse(f"/clanek/{comment.article_id}/diskuse", status_code=302)