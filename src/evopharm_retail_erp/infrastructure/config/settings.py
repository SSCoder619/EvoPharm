"""Typed application configuration model."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApplicationSettings:
    """Application configuration values."""

    application_name: str
    data_directory: Path
    database_url: str
    database_echo: bool = False
