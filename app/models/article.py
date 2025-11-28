from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SqEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.enums import ArticleStatus
from app.models.tag import article_tags
from app.models.user import saved_articles

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    perex = Column(String)     # Krátký úvod
    content = Column(Text)     # Hlavní obsah
    image_url = Column(String, nullable=True)
    
    # OPRAVA: Použití timezone-aware času i pro update
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    status = Column(SqEnum(ArticleStatus), default=ArticleStatus.DRAFT)

    # Cizí klíče
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relace
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    comments = relationship("Comment", back_populates="article")
    versions = relationship("ArticleVersion", backref="article")
    
    # Relace pro uložené články (Saved by users)
    saved_by_users = relationship("User", secondary=saved_articles, back_populates="saved_articles_rel")