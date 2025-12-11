from sqlalchemy.orm import Session
from app.models.vote import Vote

class VoteRepository:
    def get_vote(self, db: Session, user_id: int, comment_id: int):
        return db.query(Vote).filter(Vote.user_id == user_id, Vote.comment_id == comment_id).first()

    def get_user_votes(self, db: Session, user_id: int):
        return db.query(Vote).filter(Vote.user_id == user_id).all()

    def count_likes(self, db: Session, comment_id: int):
        return db.query(Vote).filter(Vote.comment_id == comment_id, Vote.vote_type == "up").count()

    def count_dislikes(self, db: Session, comment_id: int):
        return db.query(Vote).filter(Vote.comment_id == comment_id, Vote.vote_type == "down").count()

    def create(self, db: Session, vote: Vote):
        db.add(vote)
        db.commit()

    def delete(self, db: Session, vote: Vote):
        db.delete(vote)
        db.commit()

    def delete_by_user(self, db: Session, user_id: int):
        db.query(Vote).filter(Vote.user_id == user_id).delete()
        db.commit()