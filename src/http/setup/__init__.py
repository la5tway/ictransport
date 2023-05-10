from .api import setup_api
from .crawler import setup_crawler
from .db import setup_db
from .dependencies import setup_dependencies
from .orm_mapping import setup_orm_mapping

__all__ = (
    "setup_dependencies",
    "setup_orm_mapping",
    "setup_api",
    "setup_db",
    "setup_crawler",
)
