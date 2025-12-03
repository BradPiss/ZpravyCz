from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref # <--- PŘIDÁN IMPORT backref
from datetime import datetime, timezone
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_visible = Column(Boolean, default=True)
    
    # Počítadla
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)

    author_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    
    # Hierarchie (Odpověď na jiný komentář)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    author = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")
    
    # OPRAVENÁ DEFINICE: Používáme backref() helper, ne relationship()
    replies = relationship(
        "Comment", 
        backref=backref("parent", remote_side=[id]), 
        cascade="all, delete"
    )