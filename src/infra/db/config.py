from dataclasses import dataclass


@dataclass(slots=True)
class DbConfig:
    type: str
    host: str
    port: str
    name: str
    user: str
    password: str

    def __post_init__(self):
        if self.type != "postgres":
            raise RuntimeError(
                (
                    "Value of `type` variable expected is `postgres`, "
                    f"but received `{self.type}`"
                )
            )

    @property
    def url(self):
        return (
            "postgresql+asyncpg://"
            f"{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )
