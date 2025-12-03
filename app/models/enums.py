from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    CHIEF_EDITOR = "chief_editor" # <--- TOTO TAM CHYBĚLO
    EDITOR = "editor"
    READER = "reader"

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending" # <--- TOTO SE BUDE HODIT PRO SCHVALOVÁNÍ
    PUBLISHED = "published"
    ARCHIVED = "archived"