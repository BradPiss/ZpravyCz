from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Enum as SqEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.enums import Role

# Tabulka pro M:N vazbu (Uživatelé si ukládají články)
saved_articles = Table(
    "saved_articles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    
    # OPRAVA: Použití timezone-aware času
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    role = Column(SqEnum(Role), default=Role.READER)

    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    
    # Oblíbené články (M:N)
    saved_articles_rel = relationship("Article", secondary=saved_articles, back_populates="saved_by_users")