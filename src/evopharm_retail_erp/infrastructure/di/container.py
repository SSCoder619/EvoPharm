"""Dependency-injection composition root."""

from evopharm_retail_erp.infrastructure.config.settings import ApplicationSettings
from evopharm_retail_erp.infrastructure.database.configuration import DatabaseConfiguration
from evopharm_retail_erp.infrastructure.database.dependencies import DatabaseDependencies


class ServiceContainer:
    """Application dependency container with database foundation services."""

    def __init__(self, settings: ApplicationSettings) -> None:
        """Compose reusable infrastructure dependencies from application settings."""

        self.settings = settings
        configuration = DatabaseConfiguration(
            url=settings.database_url,
            echo=settings.database_echo,
        )
        self.database = DatabaseDependencies.create(configuration)
