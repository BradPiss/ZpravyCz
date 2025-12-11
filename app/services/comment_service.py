from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.repositories.comment_repository import CommentRepository
from app.repositories.vote_repository import VoteRepository
from app.models.comment import Comment
from app.models.vote import Vote

class CommentService:
    def __init__(self):
        self.repo = CommentRepository()
        self.vote_repo = VoteRepository()

    def get_tree(self, db: Session, article_id: int, user_id: int = None):
        comments = self.repo.get_visible_by_article(db, article_id)
        
        # Nacte hlasy uzivatele
        user_votes = {}
        if user_id:
            votes = self.vote_repo.get_user_votes(db, user_id)
            user_votes = {v.comment_id: v.vote_type for v in votes}
        
        replies_map = {}
        for c in comments:
            # Priradi se informace o hlasu uzivatele
            vote = user_votes.get(c.id)
            # Pokud dal lajk, ale pocet lajku je 0 kvuli chybe v DB, tak se to nezobrazi
            if (vote == 'up' and c.likes == 0) or (vote == 'down' and c.dislikes == 0): 
                vote = None
            c.user_vote = vote
            
            c.children = []
            if c.parent_id:
                if c.parent_id not in replies_map: 
                    replies_map[c.parent_id] = []
                replies_map[c.parent_id].insert(0, c)
                
        for c in comments:
            c.children = replies_map.get(c.id, [])
            
        return [c for c in comments if c.parent_id is None]

    def add(self, db: Session, content: str, article_id: int, user_id: int, parent_id: int = None):
        comment = Comment(
            content=content, 
            article_id=article_id, 
            author_id=user_id, 
            parent_id=parent_id, 
            created_at=datetime.now(timezone.utc),
            is_visible=True
        )
        return self.repo.create(db, comment)

    def vote(self, db: Session, comment_id: int, user_id: int, vote_type: str):
        comment = self.repo.get_by_id(db, comment_id)
        if not comment: return None
        
        existing = self.vote_repo.get_vote(db, user_id, comment_id)
        current = "none"
        
        if existing:
            if existing.vote_type == vote_type: 
                # Zrusi hlas
                self.vote_repo.delete(db, existing)
            else:
                # Meni hlas
                existing.vote_type = vote_type
                db.commit()
                current = vote_type
        else:
            # Novy hlas
            self.vote_repo.create(db, Vote(user_id=user_id, comment_id=comment_id, vote_type=vote_type))
            current = vote_type
            
        # Aktualizace poctu hlasu u komentare
        comment.likes = self.vote_repo.count_likes(db, comment_id)
        comment.dislikes = self.vote_repo.count_dislikes(db, comment_id)
        db.commit()
        
        return {"likes": comment.likes, "dislikes": comment.dislikes, "user_vote": current}

    def delete_comment(self, db: Session, comment_id: int, user):
        comment = self.repo.get_by_id(db, comment_id)
        if not comment: return None
        
        is_admin = user.role.value == 'admin'
        is_author = user.id == comment.author_id
        
        if is_admin or is_author:
            article_id = comment.article_id
            self.repo.delete(db, comment)
            return article_id
            
        return None