from sqlalchemy.orm import Session
from app.models.comment import Comment

class CommentRepository:
    def get_visible_by_article(self, db: Session, article_id: int):
        return db.query(Comment).filter(Comment.article_id == article_id, Comment.is_visible == True).order_by(Comment.created_at.asc()).all()

    def count_visible(self, db: Session, article_id: int):
        return db.query(Comment).filter(Comment.article_id == article_id, Comment.is_visible == True).count()

    def get_by_id(self, db: Session, comment_id: int):
        return db.query(Comment).filter(Comment.id == comment_id).first()

    def create(self, db: Session, comment: Comment):
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def delete(self, db: Session, comment: Comment):
        db.delete(comment)
        db.commit()