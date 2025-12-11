from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.db import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    articles = relationship("Article", back_populates="category")