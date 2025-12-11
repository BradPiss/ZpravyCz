from sqlalchemy.orm import Session
from app.models.category import Category

class CategoryRepository:
    def get_all(self, db: Session):
        return db.query(Category).all()
    
    def get_by_id(self, db: Session, category_id: int):
        return db.query(Category).filter(Category.id == category_id).first()