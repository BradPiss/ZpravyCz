from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.repositories.article_repository import ArticleRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.vote_repository import VoteRepository
from app.models.article import Article
from app.models.enums import ArticleStatus

class ArticleService:
    def __init__(self):
        self.repo = ArticleRepository()
        self.cat_repo = CategoryRepository()
        self.comment_repo = CommentRepository()
        self.vote_repo = VoteRepository() # Kvůli mazání článku (smazat i hlasy)

    # --- READ (Home & Detail) ---
    def get_homepage_data(self, db: Session):
        main_article = self.repo.get_published_by_position(db, 1)
        
        secondary_db = self.repo.get_published_by_positions(db, [2, 3, 4])
        pos_map = {a.home_position: a for a in secondary_db}
        promoted_articles = [pos_map.get(i) for i in [2, 3, 4]]

        list_articles = self.repo.get_latest_published(db, limit=50)

        if not main_article:
            fallback = self.repo.get_fallback_main(db)
            if fallback:
                main_article = fallback

        if not main_article and list_articles:
            main_article = list_articles.pop(0)

        exclude_ids = [a.id for a in promoted_articles if a]
        if main_article:
            exclude_ids.append(main_article.id)
            
        list_articles = self.repo.get_latest_published(db, limit=50, exclude_ids=exclude_ids)

        return {
            "main_article": main_article,
            "promoted_articles": promoted_articles,
            "list_articles": list_articles
        }

    # TATO METODA TI CHYBĚLA:
    def get_detail(self, db: Session, article_id: int):
        article = self.repo.get_by_id(db, article_id)
        if not article:
            return None
        
        comments_count = self.comment_repo.count_visible(db, article_id)
        
        # Související články
        related = self.repo.get_latest_published(db, limit=4, exclude_ids=[article_id])
        if article.category_id:
            related = [a for a in related if a.category_id == article.category_id][:4]
        
        return {
            "article": article,
            "comments_count": comments_count,
            "total_count": comments_count,
            "related_articles": related
        }

    def get_category_detail(self, db: Session, category_id: int):
        category = self.cat_repo.get_by_id(db, category_id)
        if not category:
            return None
        
        articles = [a for a in category.articles if a.status == ArticleStatus.PUBLISHED]
        articles.sort(key=lambda x: x.created_at, reverse=True)
        
        return {"category": category, "articles": articles}

    def search(self, db: Session, query: str):
        return self.repo.search(db, query)

    # --- WRITE (Admin) ---
    def create_article(self, db: Session, data: dict, user_id: int):
        # Logika pro home_position
        if data.get('home_position', 0) > 0 and data.get('status') == ArticleStatus.PUBLISHED.value:
            old = self.repo.get_published_by_position(db, data['home_position'])
            if old:
                old.home_position = 0
                db.add(old)
        
        if data.get('status') != ArticleStatus.PUBLISHED.value:
            data['home_position'] = 0

        last_promoted = datetime.now(timezone.utc) if data.get('home_position') == 1 else None

        new_article = Article(
            title=data['title'],
            perex=data['perex'],
            content=data['content'],
            category_id=data['category_id'],
            image_url=data.get('image_url'),
            image_caption=data.get('image_caption'),
            status=data['status'],
            home_position=data.get('home_position', 0),
            last_promoted_at=last_promoted,
            author_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        if data.get('tags'):
            new_article.tags = self._process_tags(db, data['tags'])
            
        return self.repo.create(db, new_article)

    def update_article(self, db: Session, article_id: int, data: dict):
        article = self.repo.get_by_id(db, article_id)
        if not article: return None

        if data.get('status') == ArticleStatus.PUBLISHED.value and data.get('home_position', 0) > 0:
            old = self.repo.get_published_by_position(db, data['home_position'])
            if old and old.id != article.id:
                old.home_position = 0
                db.add(old)
        
        for key, value in data.items():
            if key == 'tags':
                article.tags = self._process_tags(db, value)
            elif hasattr(article, key):
                setattr(article, key, value)
        
        article.updated_at = datetime.now(timezone.utc)
        db.commit()
        return article

    def delete_article(self, db: Session, article_id: int):
        article = self.repo.get_by_id(db, article_id)
        if article:
            self.repo.delete(db, article)
            return True
        return False

    def toggle_favorite(self, db: Session, user, article_id: int):
        article = self.repo.get_by_id(db, article_id)
        if not article: return None
        
        if article in user.saved_articles_rel:
            user.saved_articles_rel.remove(article)
            action = "removed"
        else:
            user.saved_articles_rel.append(article)
            action = "added"
        db.commit()
        return action

    def _process_tags(self, db: Session, tags_str: str):
        if not tags_str: return []
        names = list(set([t.strip() for t in tags_str.split(",") if t.strip()]))
        return [self.repo.get_or_create_tag(db, name) for name in names]