import datetime
from dataclasses import dataclass


@dataclass(slots=True)
class NewsEntryFromRss:
    id: str
    title: str
    preview_url: str
    pub_date: datetime.datetime
    parsed_date: datetime.datetime
