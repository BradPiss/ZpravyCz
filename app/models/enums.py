from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    CHIEF_EDITOR = "chief_editor"
    EDITOR = "editor"
    READER = "reader"

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived" ## Zatim se nepouziva