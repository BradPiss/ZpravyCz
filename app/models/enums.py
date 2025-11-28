from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    READER = "reader"


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    ARCHIVED = "archived"
