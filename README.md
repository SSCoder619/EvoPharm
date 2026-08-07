# EvoPharm Retail ERP

Commercial desktop retail ERP framework for EvoPharm.

## Architecture

The codebase follows Clean Architecture. Presentation depends on application
contracts; the application layer coordinates use cases through domain ports;
infrastructure implements external concerns such as persistence and logging.

The Medicine Catalogue is the first implemented vertical slice. Its aggregate
and immutable value objects live in `domain/medicine`, registration is an
application service, and the in-memory repository plus file audit sink are
infrastructure adapters. SQLAlchemy schema persistence remains a future
adapter, so the domain stays independent of ORM models and database lifecycle.

## Layout

```text
src/evopharm_retail_erp/
  application/      Use cases and input commands
  domain/           Business aggregates, value objects, and repository ports
  infrastructure/   Configuration, database, logging, DI, and adapters
  presentation/     PySide6 window, navigation, theme, and page shells
```

No database tables or sample data are included. The current in-memory adapter
supports local composition and application-service testing without coupling the
domain to SQLAlchemy.
