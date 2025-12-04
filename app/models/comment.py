from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timezone
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_visible = Column(Boolean, default=True)
    
    # Počítadla (jen pro rychlé čtení)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)

    author_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    author = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")
    
    # 1. FIX PRO ODPOVĚDI: Kaskádové mazání (Smažeš komentář -> smažou se odpovědi)
    replies = relationship(
        "Comment", 
        backref=backref("parent", remote_side=[id]), 
        cascade="all, delete-orphan" 
    )

    # 2. FIX PRO LAJKY (TOTO JE TO HLAVNÍ):
    # Definujeme vztah k Vote a říkáme: "Když smažeš mě, smaž i moje lajky"
    votes_rel = relationship(
        "Vote",
        backref="comment",
        cascade="all, delete-orphan"
    )