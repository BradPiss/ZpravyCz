from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    READER = "reader"

class ArticleStatus(str, Enum):
    DRAFT = "draft"         # Rozepsané
    PENDING = "pending"     # Čeká na schválení
    PUBLISHED = "published" # Vydáno
    ARCHIVED = "archived"   # Staženo