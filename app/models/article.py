from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from app.models.enums import ArticleStatus
from app.models.tag import article_tags


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    perex = Column(String(500))
    content = Column(Text)
    image_url = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT)
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, backref="articles")
    comments = relationship("Comment", back_populates="article")
    versions = relationship("ArticleVersion", back_populates="article")
