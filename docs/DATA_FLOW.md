# EvoPharm Retail ERP — Data Flow

## Flow design principles

Commercial documents capture a point-in-time record. Their finalized line items identify a medicine batch. Inventory-impacting events create stock-movement ledger entries, which update the current inventory projection. Reporting consumes retained document, ledger, and projection data without becoming a source of operational data.

## Purchase flow

```mermaid
flowchart TD
    A[Supplier] --> B[Purchase]
    B --> C[Purchase Item]
    C --> D[Medicine Batch]
    D --> E[Stock Movement: receipt]
    E --> F[Inventory]
    B --> G[Purchase reporting view]
    E --> G
```

The purchase captures supplier and financial details. Each item establishes or references a batch. A receipt movement provides the traceable stock effect, and inventory becomes the current-stock projection.

## Sales flow

```mermaid
flowchart TD
    A[Customer, optional] --> B[Sale]
    C[Inventory availability] --> D[Sale Item]
    B --> D
    E[Medicine Batch] --> D
    D --> F[Stock Movement: issue]
    F --> G[Inventory]
    B --> H[Sales reporting view]
    F --> H
```

The sale retains a customer only when applicable. Each sale item identifies the batch issued. The issue movement reduces the inventory projection and preserves the source invoice reference for analysis and traceability.

## Return flow

```mermaid
flowchart TD
    A[Original Purchase] --> B[Purchase Return]
    B --> C[Purchase Return Item]
    C --> D[Stock Movement: supplier return]
    D --> E[Inventory]

    F[Original Sale] --> G[Sale Return]
    G --> H[Sale Return Item]
    H --> I[Return disposition]
    I --> J[Stock Movement: accepted return]
    J --> E
```

Both return types retain an explicit link to their original commercial document and item. A supplier return removes batch stock. A customer return records a restock disposition before its inventory effect is represented in the ledger.

## Inventory flow

```mermaid
flowchart LR
    A[Purchase receipt] --> E[Stock Movement Ledger]
    B[Sale issue] --> E
    C[Supplier return] --> E
    D[Customer return] --> E
    E --> F[Inventory by Medicine Batch]
    F --> G[Availability and expiry views]
    E --> H[Reconciliation and valuation views]
```

Inventory is not the source of the stock history. The stock-movement ledger is the traceable event record; inventory is the current per-batch state derived from it.

## Reporting flow

```mermaid
flowchart TD
    A[Purchases and purchase items] --> E[Reporting dataset]
    B[Sales and sale items] --> E
    C[Returns] --> E
    D[Stock movements and inventory] --> E
    F[GST categories] --> E
    E --> G[Sales analysis]
    E --> H[Purchase analysis]
    E --> I[Inventory and expiry analysis]
    E --> J[GST analysis]
    E --> K[Audit and traceability analysis]
```

Reports are read-oriented outputs. They consume authoritative persisted records and do not create or modify commercial, inventory, or master data.
