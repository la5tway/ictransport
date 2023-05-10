from src.domain.news import NewsEntry
from src.infra.db.models import NewsEntryModel
from src.infra.db.models.base import registry


def setup_orm_mapping():
    registry.map_imperatively(
        NewsEntry,
        NewsEntryModel.__table__,
    )
