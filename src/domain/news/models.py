import datetime
from dataclasses import dataclass


@dataclass
class NewsEntry:
    id: str
    tag: str
    title: str
    preview_url: str
    pub_date: datetime.datetime
    parsed_date: datetime.datetime
