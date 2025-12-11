from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.models.article import Article
from app.models.enums import ArticleStatus
from app.models.tag import Tag

class ArticleRepository:
    def get_by_id(self, db: Session, article_id: int):
        return db.query(Article).filter(Article.id == article_id).first()

    def get_all_admin(self, db: Session):
        return db.query(Article).order_by(desc(Article.created_at)).all()

    def get_published_by_position(self, db: Session, position: int):
        return db.query(Article).filter(Article.home_position == position, Article.status == ArticleStatus.PUBLISHED).first()

    def get_published_by_positions(self, db: Session, positions: list[int]):
        return db.query(Article).filter(Article.home_position.in_(positions), Article.status == ArticleStatus.PUBLISHED).all()

    def get_latest_published(self, db: Session, limit: int = 50, exclude_ids: list[int] = None):
        query = db.query(Article).filter(Article.status == ArticleStatus.PUBLISHED, Article.home_position == 0)
        if exclude_ids:
            query = query.filter(Article.id.notin_(exclude_ids))
        return query.order_by(desc(Article.created_at)).limit(limit).all()

    def get_fallback_main(self, db: Session):
        return db.query(Article).filter(Article.status == ArticleStatus.PUBLISHED, Article.last_promoted_at != None, Article.home_position == 0).order_by(desc(Article.last_promoted_at)).first()

    def search(self, db: Session, query: str):
        return db.query(Article).outerjoin(Article.tags).filter(Article.status == ArticleStatus.PUBLISHED, or_(Article.title.contains(query), Article.perex.contains(query), Tag.name.contains(query))).distinct().order_by(desc(Article.created_at)).all()

    def create(self, db: Session, article: Article):
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    def delete(self, db: Session, article: Article):
        db.delete(article)
        db.commit()

    def get_or_create_tag(self, db: Session, name: str):
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        return tag
    
    def get_by_category(self, db: Session, category_id: int, limit: int = 4, exclude_id: int = None):
        query = db.query(Article).filter(
            Article.status == ArticleStatus.PUBLISHED,
            Article.category_id == category_id
        )
        
        if exclude_id:
            query = query.filter(Article.id != exclude_id)
            
        return query.order_by(desc(Article.created_at)).limit(limit).all()