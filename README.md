# EvoPharm Retail ERP

Commercial desktop retail ERP framework for EvoPharm.

## Architecture

The codebase follows Clean Architecture. Presentation depends on application contracts; infrastructure provides configuration, persistence, logging, and composition boundaries. Domain, services, repositories, controllers, and UI pages are intentionally empty framework contracts.

## Layout

```text
src/evopharm_retail_erp/
  application/      Use-case boundary contracts
  domain/           Domain service and repository contracts
  infrastructure/   Configuration, database, logging, and DI boundaries
  presentation/     PySide6 window, navigation, theme, and page shells
```

No business features, database tables, sample data, or feature logic are included.
