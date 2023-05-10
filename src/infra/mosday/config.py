from dataclasses import dataclass


@dataclass(slots=True)
class CrawlerConfig:
    delay_minutes: float = 15
    delay_seconds: float = 0

    parse_days: int = 2

    def __post_init__(self):
        if not self.delay_seconds:
            self.delay_seconds = self.delay_minutes * 60
