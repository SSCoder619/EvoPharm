"""
Domain Services for the Medicine bounded context in EvoPharm Retail ERP.

Architectural Assessment (Domain-Driven Design):
------------------------------------------------
Domain Services in DDD are intended strictly for domain logic that:
1. Involves multiple aggregates that cannot be naturally combined.
2. Represents a standalone domain transformation or business process that does
   not belong to a single Entity or Value Object.

Within the Medicine bounded context:
- All state invariants, validations, and state transition rules are fully
  encapsulated within the `Medicine` Aggregate Root (`entities.py`).
- Cross-attribute business query predicates are encapsulated in stateless
  Domain Specifications (`specifications.py`).
- Value Object encapsulation ensures valid domain primitives (`value_objects.py`).

Creating a generic `MedicineService` or CRUD wrapper service would introduce an anemic
domain model and violate aggregate boundaries. Therefore, no Domain Services are currently
required for this bounded context.
"""

from __future__ import annotations

# Module intentionally left without stateful or anemic wrapper classes.
# All core business rules and behavior reside within the Medicine aggregate root and specifications.