from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password
from app.models.user import User
from app.models.enums import Role

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