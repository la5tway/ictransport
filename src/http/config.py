from dataclasses import dataclass

from src.config import AppConfig
from src.infra.db.config import DbConfig
from src.infra.mosday.config import CrawlerConfig


@dataclass(slots=True)
class HttpConfig:
    host: str = "127.0.0.1"
    port: int = 80


@dataclass(slots=True)
class Config:
    db: DbConfig
    app: AppConfig
    crawler: CrawlerConfig
    http: HttpConfig
