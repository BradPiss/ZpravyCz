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
    perex = Column(String)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    
    # Časy
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Stav (Koncept / Vydáno)
    status = Column(SqEnum(ArticleStatus), default=ArticleStatus.DRAFT)
    
    # --- NOVÉ SLOUPCE PRO POZICE ---
    # 0=Seznam, 1=Hlavní, 2=Vlevo, 3=Střed, 4=Vpravo
    home_position = Column(Integer, default=0, index=True)
    
    # Kdy byl naposledy na pozici 1 (pro historii a automatické doplnění)
    last_promoted_at = Column(DateTime, nullable=True)
    # -------------------------------

    # Cizí klíče
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relace
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    comments = relationship("Comment", back_populates="article")
    versions = relationship("ArticleVersion", backref="article")
    saved_by_users = relationship("User", secondary=saved_articles, back_populates="saved_articles_rel")