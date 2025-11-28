from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ArticleVersion(Base):
    __tablename__ = "article_versions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    version_number = Column(Integer)
    title = Column(String)
    content = Column(Text)
    perex = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="versions")
