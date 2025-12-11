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
        user_votes = {v.comment_id: v.vote_type for v in self.vote_repo.get_user_votes(db, user_id)} if user_id else {}
        
        replies_map = {}
        for c in comments:
            vote = user_votes.get(c.id)
            if (vote == 'up' and c.likes == 0) or (vote == 'down' and c.dislikes == 0): vote = None
            c.user_vote = vote
            c.children = []
            if c.parent_id:
                if c.parent_id not in replies_map: replies_map[c.parent_id] = []
                replies_map[c.parent_id].insert(0, c)
                
        for c in comments:
            c.children = replies_map.get(c.id, [])
            
        return [c for c in comments if c.parent_id is None]

    def add(self, db: Session, content: str, article_id: int, user_id: int, parent_id: int = None):
        return self.repo.create(db, Comment(content=content, article_id=article_id, author_id=user_id, parent_id=parent_id, created_at=datetime.now(timezone.utc)))

    def vote(self, db: Session, comment_id: int, user_id: int, vote_type: str):
        comment = self.repo.get_by_id(db, comment_id)
        if not comment: return None
        
        existing = self.vote_repo.get_vote(db, user_id, comment_id)
        current = "none"
        
        if existing:
            if existing.vote_type == vote_type: self.vote_repo.delete(db, existing)
            else:
                existing.vote_type = vote_type
                db.commit()
                current = vote_type
        else:
            self.vote_repo.create(db, Vote(user_id=user_id, comment_id=comment_id, vote_type=vote_type))
            current = vote_type
            
        comment.likes = self.vote_repo.count_likes(db, comment_id)
        comment.dislikes = self.vote_repo.count_dislikes(db, comment_id)
        db.commit()
        
        return {"likes": comment.likes, "dislikes": comment.dislikes, "user_vote": current}