import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Model


class NewsEntryModel(Model):
    __tablename__ = "news"

    id: Mapped[str] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    pub_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    parsed_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    preview_url: Mapped[str]
