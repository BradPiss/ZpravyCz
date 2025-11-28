from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    
    # OPRAVA: Použití timezone-aware času
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    is_visible = Column(Boolean, default=True)

    author_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    
    # Odpovědi na komentáře (rodič)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    author = relationship("User", back_populates="comments")
    
    # TADY BYLA CHYBA - opraveno na "comments"
    article = relationship("Article", back_populates="comments")