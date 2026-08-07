from pathlib import Path

# Root of the project
ROOT = Path(__file__).parent

directories = [
    "tests",

    "tests/fixtures",
    "tests/builders",

    "tests/domain",
    "tests/domain/medicine",
    "tests/domain/inventory",
    "tests/domain/supplier",
    "tests/domain/customer",
    "tests/domain/purchase",
    "tests/domain/sales",
    "tests/domain/invoice",
    "tests/domain/users",

    "tests/application",
    "tests/application/medicine",
    "tests/application/inventory",
    "tests/application/purchase",
    "tests/application/sales",
    "tests/application/invoice",

    "tests/infrastructure",
    "tests/infrastructure/persistence",
    "tests/infrastructure/cache",
    "tests/infrastructure/events",
    "tests/infrastructure/messaging",

    "tests/presentation",
    "tests/presentation/api",
    "tests/presentation/cli",

    "tests/integration",
    "tests/integration/medicine",
    "tests/integration/inventory",
    "tests/integration/purchase",
    "tests/integration/sales",
    "tests/integration/billing",

    "tests/contract",

    "tests/performance",

    "tests/security",

    "tests/regression",

    "tests/smoke",

    "tests/e2e",
]

files = [
    "tests/__init__.py",
    "tests/conftest.py",

    # Fixtures
    "tests/fixtures/__init__.py",
    "tests/fixtures/medicine.py",
    "tests/fixtures/medicine_batch.py",
    "tests/fixtures/inventory.py",
    "tests/fixtures/supplier.py",
    "tests/fixtures/customer.py",
    "tests/fixtures/purchase.py",
    "tests/fixtures/sales.py",
    "tests/fixtures/invoice.py",
    "tests/fixtures/users.py",

    # Builders
    "tests/builders/__init__.py",
    "tests/builders/medicine_builder.py",
    "tests/builders/medicine_batch_builder.py",
    "tests/builders/inventory_builder.py",
    "tests/builders/purchase_builder.py",
    "tests/builders/sales_builder.py",
    "tests/builders/supplier_builder.py",

    # Domain - Medicine
    "tests/domain/medicine/test_entities.py",
    "tests/domain/medicine/test_value_objects.py",
    "tests/domain/medicine/test_enums.py",
    "tests/domain/medicine/test_exceptions.py",
    "tests/domain/medicine/test_interfaces.py",
    "tests/domain/medicine/test_domain_events.py",
    "tests/domain/medicine/test_specifications.py",
    "tests/domain/medicine/test_policies.py",

    # Domain - Inventory
    "tests/domain/inventory/test_entities.py",
    "tests/domain/inventory/test_value_objects.py",
    "tests/domain/inventory/test_services.py",
    "tests/domain/inventory/test_policies.py",

    # Domain - Supplier
    "tests/domain/supplier/test_entities.py",
    "tests/domain/supplier/test_value_objects.py",

    # Domain - Customer
    "tests/domain/customer/test_entities.py",
    "tests/domain/customer/test_value_objects.py",

    # Domain - Purchase
    "tests/domain/purchase/test_entities.py",
    "tests/domain/purchase/test_services.py",
    "tests/domain/purchase/test_policies.py",

    # Domain - Sales
    "tests/domain/sales/test_entities.py",
    "tests/domain/sales/test_services.py",
    "tests/domain/sales/test_policies.py",

    # Domain - Invoice
    "tests/domain/invoice/test_entities.py",
    "tests/domain/invoice/test_value_objects.py",

    # Domain - Users
    "tests/domain/users/test_entities.py",
    "tests/domain/users/test_value_objects.py",

    # Application
    "tests/application/medicine/test_commands.py",
    "tests/application/medicine/test_command_handlers.py",
    "tests/application/medicine/test_queries.py",
    "tests/application/medicine/test_query_handlers.py",
    "tests/application/medicine/test_dtos.py",
    "tests/application/medicine/test_validators.py",

    # Infrastructure
    "tests/infrastructure/persistence/test_sqlalchemy_repository.py",
    "tests/infrastructure/persistence/test_sqlite_repository.py",
    "tests/infrastructure/persistence/test_postgres_repository.py",
    "tests/infrastructure/persistence/test_unit_of_work.py",

    "tests/infrastructure/cache/test_redis.py",

    "tests/infrastructure/events/test_event_bus.py",

    "tests/infrastructure/messaging/test_message_bus.py",

    # Presentation
    "tests/presentation/api/test_medicine_api.py",
    "tests/presentation/api/test_inventory_api.py",
    "tests/presentation/api/test_sales_api.py",
    "tests/presentation/api/test_purchase_api.py",

    "tests/presentation/cli/test_cli.py",

    # Integration
    "tests/integration/medicine/test_receive_batch.py",
    "tests/integration/medicine/test_recall_batch.py",
    "tests/integration/medicine/test_quarantine_batch.py",
    "tests/integration/medicine/test_expiry.py",

    # Contract
    "tests/contract/test_repository_contract.py",
    "tests/contract/test_event_contract.py",
    "tests/contract/test_api_contract.py",

    # Performance
    "tests/performance/test_batch_lookup.py",
    "tests/performance/test_fefo.py",
    "tests/performance/test_barcode_lookup.py",
    "tests/performance/test_inventory_scalability.py",

    # Security
    "tests/security/test_permissions.py",
    "tests/security/test_authentication.py",
    "tests/security/test_authorization.py",

    # Regression
    "tests/regression/test_issue_001.py",
    "tests/regression/test_issue_002.py",
    "tests/regression/test_issue_003.py",

    # Smoke
    "tests/smoke/test_startup.py",
    "tests/smoke/test_database.py",
    "tests/smoke/test_endpoints.py",

    # End-to-End
    "tests/e2e/test_complete_sale.py",
    "tests/e2e/test_complete_purchase.py",
    "tests/e2e/test_batch_recall.py",
    "tests/e2e/test_inventory_flow.py",
    "tests/e2e/test_pharmacy_workflow.py",
]

# Create directories
for directory in directories:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    path = ROOT / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("=" * 60)
print(" EvoPharm Test Structure Created Successfully")
print("=" * 60)
print(f"Directories created : {len(directories)}")
print(f"Files created       : {len(files)}")
print("=" * 60)