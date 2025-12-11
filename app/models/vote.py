from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.db import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    vote_type = Column(String) # up nebo down