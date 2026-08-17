# EvoPharm Retail ERP — Bug & Audit Register

This document tracks all identified bugs, technical debt items, architectural inconsistencies, deprecation warnings, and planned future infrastructure tasks discovered during system audits.

> [!IMPORTANT]
> **Audit Policy**: This register contains findings from read-only architectural and code quality audits. Code modifications in production (`src/`) and test (`tests/`) modules must be scheduled and executed through formal engineering phases.

---

## Severity & Category Index

| Category / Classification | Description | Count |
|---|---|---|
| **P0** | Critical / System-blocking defect. Prevents build or execution. | 0 |
| **P1** | High severity bug. Core business logic failure or data loss risk. | 0 |
| **P2** | Medium severity defect. Non-critical functionality defect or edge-case failure. | 0 |
| **P3** | Low severity issue. Minor operational anomaly or sub-optimal exception handling. | 2 |
| **TECH-DEBT** | Code maintenance, typing incomplete, naming inconsistencies, or API boilerplate. | 4 |
| **WARNING** | Upstream library deprecation warning or environment configuration hazard. | 2 |
| **FUTURE** | Planned architectural capability or progressive persistence phase item. | 1 |

---

## 1. Confirmed Findings & Technical Audit Log

### BUG-001: FastAPI / Starlette / `httpx` TestClient Deprecation Warning

- **Classification**: `WARNING` / `TECH-DEBT`
- **Component / Location**: `tests/presentation/test_*.py` (via `.venv/Lib/site-packages/fastapi/testclient.py:1`)
- **Evidence / Trace**:
  ```text
  StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa
  ```
- **Description**: When executing the presentation test suite with `pytest`, Starlette issues a deprecation warning regarding the internal binding of `httpx` within `starlette.testclient.TestClient`.
- **Impact**: Non-breaking for current runtime execution (12/12 presentation tests pass), but may cause compatibility issues when upgrading FastAPI/Starlette in future dependencies.
- **Recommendation**: Migrate API integration tests to `httpx.AsyncClient` with `ASGITransport` or update `httpx` test client dependencies upon next dependency upgrade phase.

---

### BUG-002: UnitOfWork Protocol vs Implementation Property Naming Inconsistency

- **Classification**: `P3` / `TECH-DEBT`
- **Locations**:
  - [src/evopharm_retail_erp/application/common/unit_of_work.py](file:///e:/evopharm/EvoPharm/src/evopharm_retail_erp/application/common/unit_of_work.py#L30-L60)
  - [src/evopharm_retail_erp/infrastructure/unit_of_work/sqlalchemy.py](file:///e:/evopharm/EvoPharm/src/evopharm_retail_erp/infrastructure/unit_of_work/sqlalchemy.py#L75-L105)
  - [tests/presentation/helpers.py](file:///e:/evopharm/EvoPharm/tests/presentation/helpers.py#L250-L290)
- **Evidence**:
  ```python
  # application/common/unit_of_work.py defines plural properties:
  @property
  def medicines(self) -> MedicineRepository: ...
  @property
  def suppliers(self) -> SupplierRepository: ...

  # Application services and presentation routers consume singular property aliases:
  uow.supplier.add(supplier)
  active_uow.invoice.get_by_id(...)
  ```
- **Description**: The `UnitOfWork` Protocol in `application/common` formally defines plural repository properties (`medicines`, `inventory`, `suppliers`, `purchases`, `customers`, `sales`, `invoices`). Concrete implementations (`SqlAlchemyUnitOfWork` and `InMemoryUnitOfWork`) provide singular aliases (`medicine`, `supplier`, `customer`, `sale`, `invoice`) to support application service consumption.
- **Impact**: Static type checkers enforcing strict protocol matching without duck-typing may flag property access errors when type-hinted strictly as `UnitOfWork`.
- **Recommendation**: Formally declare both plural and singular property signatures in `UnitOfWork` Protocol interface (`application/common/unit_of_work.py`).

---

### BUG-003: Direct `ApplicationResult.value` Dereferencing in API Routers

- **Classification**: `P3`
- **Locations**: Presentation API routers (`src/evopharm_retail_erp/presentation/api/routers/*.py`)
- **Evidence**:
  ```python
  result = await service.register_supplier(cmd)
  res = result.value  # Raises ValueError if result.is_success is False
  ```
- **Description**: Presentation router endpoints access `result.value` directly upon receiving an `ApplicationResult`. If an application service returns a failed result (`ApplicationResult.failure(...)`), accessing `.value` raises a `ValueError(f"Cannot access value on a failed ApplicationResult: {self.error_message}")`.
- **Impact**: The exception is caught globally by `value_error_handler` returning HTTP 400 Bad Request. However, this bypasses explicit mapping of application-level `error_code` strings (`result.error_code`) to specific HTTP status codes.
- **Recommendation**: Create a helper function `unwrap_result(result)` in presentation dependencies to check `result.is_failure` and translate `result.error_code` / `result.error_message` directly into structured `HTTPException` responses.

---

### BUG-004: Missing Return Type Annotations in Infrastructure & Presentation Modules

- **Classification**: `TECH-DEBT`
- **Locations**:
  - `src/evopharm_retail_erp/infrastructure/repositories/medicine.py` (Line 33, `_query` helper method)
  - `src/evopharm_retail_erp/infrastructure/database/dependencies.py` (Line 32, `get_session_factory` helper method)
- **Evidence**:
  Output from `tools/vv.py` static typing analyzer:
  ```text
  Total Functions Checked:    1026
  Annotated Functions:       1024 (99.8%)
  Missing Return Annotations: 2
  Status:                    [WARN]
  ```
- **Description**: Static AST inspection detected two helper functions missing explicit return type annotations (`_query` and `get_session_factory`).
- **Impact**: Minor reduction in static typing completeness (99.8% annotated vs 100.0% clean target).
- **Recommendation**: Add explicit `-> Select[Tuple[MedicineORM]]` and `-> async_sessionmaker[AsyncSession]` return annotations.

---

### BUG-005: Explicit `Any` Type Reference in Database Engine Module

- **Classification**: `TECH-DEBT`
- **Location**: `src/evopharm_retail_erp/infrastructure/database/engine.py` (Line 24)
- **Evidence**:
  ```python
  # Explicit 'Any' reference detected during static AST type inspection
  ```
- **Description**: An explicit `Any` import and type annotation is present in the database engine event listener / configuration setup.
- **Impact**: Bypasses strict static type checking for database connection hook signatures.
- **Recommendation**: Replace `Any` with specific SQLAlchemy connection pool / event type annotations (e.g. `Pool`, `Connection`).

---

### BUG-006: SQLite In-Memory Database Isolation in Development/Testing Mode

- **Classification**: `WARNING` / `TECH-DEBT`
- **Locations**:
  - `src/evopharm_retail_erp/infrastructure/database/session.py`
  - `src/evopharm_retail_erp/infrastructure/database/config.py`
- **Evidence**:
  ```python
  DATABASE_URL = "sqlite+aiosqlite:///:memory:"
  ```
- **Description**: Default fallback database configuration uses `sqlite+aiosqlite:///:memory:`. SQLite in-memory databases create separate empty database instances per connection unless an explicit shared cache (`cache=shared`) or persistent engine connection is maintained across asynchronous tasks.
- **Impact**: Async test fixtures operating against raw ORM sessions require explicit table creation on the shared connection to prevent `OperationalError: no such table`.
- **Recommendation**: Update default dev/test connection strings to use shared-cache URI syntax (`sqlite+aiosqlite:///file:memdb?mode=memory&cache=shared`) or PostgreSQL test containers.

---

### BUG-007: Pending Persistence Mappings for Remaining Bounded Contexts

- **Classification**: `FUTURE` / `TECH-DEBT`
- **Locations**:
  - `src/evopharm_retail_erp/infrastructure/persistence/`
  - `src/evopharm_retail_erp/infrastructure/repositories/`
- **Evidence**:
  SQLAlchemy ORM models, mappers, and repository implementations are currently completed and verified for 4 bounded contexts:
  1. `Medicine` (`MedicineORM`, `SqlAlchemyMedicineRepository`)
  2. `Inventory` (`InventoryORM`, `StockMovementORM`, `SqlAlchemyInventoryRepository`)
  3. `Supplier` (`SupplierORM`, `SqlAlchemySupplierRepository`)
  4. `Purchase` (`PurchaseORM`, `PurchaseLineORM`, `SqlAlchemyPurchaseRepository`)

  `Sales`, `Customer`, and `Invoice` contexts rely on in-memory repository adapters during presentation testing.
- **Impact**: Production database persistence is complete for 4/7 contexts. Full PostgreSQL deployment requires ORM persistence for the remaining 3 contexts.
- **Recommendation**: Implement `CustomerORM`, `SaleORM`, `InvoiceORM` and corresponding SQLAlchemy repositories in upcoming Phase 5D persistence expansion.

---

## 2. Verification Audit Status

- **Architecture Boundary Violations**: `0`
- **Domain Required Structure Coverage**: `100.0%`
- **Pytest Suite Status**: `312 / 312 PASSED`
- **Toolkit Verification Result**: `RESULT: PASS` (`tools/vv.py`)

---

*Last Updated*: 2026-08-09
