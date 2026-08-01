"""Dependency-injection container boundary."""

from evopharm_retail_erp.infrastructure.config.settings import ApplicationSettings


class ServiceContainer:
    """Application dependency container contract."""

    settings: ApplicationSettings
