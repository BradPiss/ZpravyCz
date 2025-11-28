from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base

class ArticleVersion(Base):
    __tablename__ = "article_versions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    version_number = Column(Integer)
    
    title = Column(String)
    perex = Column(String)
    content = Column(Text)
    
    # OPRAVA: Použití timezone-aware času
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))