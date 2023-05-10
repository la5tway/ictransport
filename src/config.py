from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    PRODUCTION = "prod"
    DEVELOPMENT = "dev"


@dataclass(slots=True)
class AppConfig:
    environment: Environment = Environment.DEVELOPMENT

    @property
    def is_dev(self):
        return self.environment is Environment.DEVELOPMENT
