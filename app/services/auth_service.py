from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password
from app.models.user import User
from app.models.enums import Role
from app.models.article import Article
from app.models.comment import Comment
from app.models.vote import Vote

class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def authenticate(self, db: Session, email: str, password: str):
        user = self.repo.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def register(self, db: Session, email: str, password: str, name: str):
        if self.repo.get_by_email(db, email): return None
        return self.repo.create(db, User(email=email, name=name, password_hash=hash_password(password), role=Role.READER, is_active=True))
    
    def update_user(self, db: Session, user_id: int, role: str, is_active: bool):
        user = self.repo.get_by_id(db, user_id)
        if not user:
            return None
        
        user.role = role
        user.is_active = is_active
        db.commit()
        return user

    def delete_user_complex(self, db: Session, user_id_to_delete: int, admin_id: int):
        del_user = self.repo.get_by_id(db, user_id_to_delete)
        
        # Ochrana proti smazani sam sebe
        if not del_user or del_user.id == admin_id:
            return False

        # Prevod clanku na admina
        user_articles = db.query(Article).filter(Article.author_id == del_user.id).all()
        for a in user_articles: 
            a.author_id = admin_id
            
        # Smazani komentaru
        user_comments = db.query(Comment).filter(Comment.author_id == del_user.id).all()
        for c in user_comments: 
            db.delete(c)
            
        # Smazani lajku a dislajku
        db.query(Vote).filter(Vote.user_id == del_user.id).delete()
        
        # Smazani uzivatele
        self.repo.delete(db, del_user)
        return True