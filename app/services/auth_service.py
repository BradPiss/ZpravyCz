from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.article_repository import ArticleRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.vote_repository import VoteRepository
from app.core.security import verify_password, hash_password
from app.models.user import User
from app.models.enums import Role

class AuthService:
    def __init__(self):
        self.repo = UserRepository()
        self.article_repo = ArticleRepository()
        self.comment_repo = CommentRepository()
        self.vote_repo = VoteRepository()

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
        if not user: return None
        user.role = role
        user.is_active = is_active
        db.commit()
        return user

    def delete_user_complex(self, db: Session, user_id_to_delete: int, admin_id: int):
        del_user = self.repo.get_by_id(db, user_id_to_delete)
        
        if not del_user or del_user.id == admin_id:
            return False

        self.article_repo.transfer_to_user(db, del_user.id, admin_id)
        self.comment_repo.delete_by_author(db, del_user.id)
        self.vote_repo.delete_by_user(db, del_user.id)
        self.repo.delete(db, del_user)
        return True