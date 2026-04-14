import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    kafka_bootstrap_servers: str = field(
        default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
    )
    analytics_database_url: str = field(
        default_factory=lambda: os.environ["ANALYTICS_DATABASE_URL"]
    )
    topics: list[str] = field(
        default_factory=lambda: [
            "hp.products",
            "hp.orders",
            "hp.inventory",
            "hp.users",
        ]
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
