from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from app.models.enums import Role


# Association table for saved/favorite articles (M:N User-Article)
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
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(Enum(Role), default=Role.READER)

    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    saved_articles = relationship(
        "Article",
        secondary=saved_articles,
        backref="saved_by_users"
    )
