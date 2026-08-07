# EvoPharm Retail ERP — Future Database Design

## General conventions

- Each table uses a stable surrogate primary key (`id`).
- Record timestamps use `created_at` and `updated_at` where the record is mutable; immutable ledger and audit records use `occurred_at` or `recorded_at`.
- Monetary amounts use fixed-precision decimal values. Quantities use fixed-precision decimal values to support loose or partial packs where policy allows.
- Historical line data stores product description, pricing, discount, and tax snapshots. Master records are not used to reinterpret past documents.
- Master records use an active-state field instead of deletion where historical references may exist.

## Master and access-control tables

### `gst_categories`

- **Purpose:** Reusable GST classification and rate definition for medicine defaults.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `code`, `name`, `hsn_code`, `cgst_rate`, `sgst_rate`, `igst_rate`, `effective_from`, `effective_to`, `is_active`.
- **Relationships:** One category can classify many medicines.
- **Suggested indexes:** Unique `code`; `hsn_code`; composite `(is_active, effective_from, effective_to)`.

### `medicines`

- **Purpose:** Product master for a medicine independent of batches.
- **Primary key:** `id`.
- **Foreign keys:** `gst_category_id` → `gst_categories.id`.
- **Important fields:** `sku`, `barcode`, `name`, `generic_name`, `manufacturer_name`, `dosage_form`, `strength`, `pack_size`, `unit_of_measure`, `schedule_classification`, `default_sale_price`, `reorder_level`, `is_active`.
- **Relationships:** One medicine has many batches; one GST category classifies many medicines.
- **Suggested indexes:** Unique `sku`; unique nullable `barcode`; normalized `name`; `(gst_category_id, is_active)`; `(manufacturer_name, generic_name)`.

### `suppliers`

- **Purpose:** Supplier master and statutory/contact record.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `supplier_code`, `legal_name`, `trade_name`, `gstin`, `drug_license_number`, `contact_name`, `phone`, `email`, `billing_address`, `shipping_address`, `payment_terms_days`, `is_active`.
- **Relationships:** One supplier has many purchases and purchase returns.
- **Suggested indexes:** Unique `supplier_code`; unique nullable `gstin`; `legal_name`; `is_active`.

### `customers`

- **Purpose:** Optional retained customer master for retail and tax invoices.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `customer_code`, `name`, `phone`, `email`, `gstin`, `address`, `date_of_birth`, `is_active`.
- **Relationships:** One customer can have many sales and sale returns.
- **Suggested indexes:** Unique `customer_code`; unique nullable `phone`; unique nullable `gstin`; normalized `name`; `is_active`.

### `users`

- **Purpose:** User-account identity and account status.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `username`, `display_name`, `email`, `credential_reference`, `is_active`, `last_login_at`.
- **Relationships:** Many-to-many with roles through `user_roles`; one user produces many audit logs and may be recorded as document actor.
- **Suggested indexes:** Unique `username`; unique nullable `email`; `is_active`.

### `roles`

- **Purpose:** Named access-control role.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `name`, `description`, `is_system_role`, `is_active`.
- **Relationships:** Many-to-many with users and permissions.
- **Suggested indexes:** Unique `name`; `is_active`.

### `permissions`

- **Purpose:** Stable permission catalogue for authorization assignments.
- **Primary key:** `id`.
- **Foreign keys:** None.
- **Important fields:** `code`, `module`, `description`, `is_active`.
- **Relationships:** Many-to-many with roles through `role_permissions`.
- **Suggested indexes:** Unique `code`; `(module, is_active)`.

### `user_roles`

- **Purpose:** User-to-role association.
- **Primary key:** Composite `user_id`, `role_id`.
- **Foreign keys:** `user_id` → `users.id`; `role_id` → `roles.id`.
- **Important fields:** `assigned_at`, `assigned_by_user_id`.
- **Relationships:** Connects users and roles.
- **Suggested indexes:** Composite primary key; reverse `(role_id, user_id)`.

### `role_permissions`

- **Purpose:** Role-to-permission association.
- **Primary key:** Composite `role_id`, `permission_id`.
- **Foreign keys:** `role_id` → `roles.id`; `permission_id` → `permissions.id`.
- **Important fields:** `granted_at`.
- **Relationships:** Connects roles and permissions.
- **Suggested indexes:** Composite primary key; reverse `(permission_id, role_id)`.

### `settings`

- **Purpose:** Versioned application-wide configuration.
- **Primary key:** `id`.
- **Foreign keys:** Optional `updated_by_user_id` → `users.id`.
- **Important fields:** `setting_key`, `setting_value`, `value_type`, `scope`, `is_sensitive`, `updated_at`.
- **Relationships:** A user can update many settings.
- **Suggested indexes:** Unique `(scope, setting_key)`; `updated_at`.

## Commercial and inventory tables

### `medicine_batches`

- **Purpose:** Traceable supplier lot for a medicine.
- **Primary key:** `id`.
- **Foreign keys:** `medicine_id` → `medicines.id`; optional `supplier_id` → `suppliers.id`.
- **Important fields:** `batch_number`, `manufactured_on`, `expires_on`, `mrp`, `purchase_price`, `status`, `received_at`.
- **Relationships:** One medicine has many batches; one batch has one inventory projection and many line items/movements.
- **Suggested indexes:** Unique `(medicine_id, batch_number)`; `(expires_on, status)`; `(supplier_id, received_at)`.

### `purchases`

- **Purpose:** Supplier purchase document header.
- **Primary key:** `id`.
- **Foreign keys:** `supplier_id` → `suppliers.id`; `created_by_user_id` → `users.id`.
- **Important fields:** `purchase_number`, `supplier_invoice_number`, `purchase_date`, `due_date`, `status`, `subtotal`, `discount_total`, `tax_total`, `rounding_amount`, `grand_total`, `notes`.
- **Relationships:** One supplier has many purchases; a purchase has many purchase items and may have many purchase returns.
- **Suggested indexes:** Unique `purchase_number`; unique `(supplier_id, supplier_invoice_number)` when present; `(supplier_id, purchase_date)`; `(status, purchase_date)`.

### `purchase_items`

- **Purpose:** Batch-specific purchase document line.
- **Primary key:** `id`.
- **Foreign keys:** `purchase_id` → `purchases.id`; `medicine_id` → `medicines.id`; `medicine_batch_id` → `medicine_batches.id`; `gst_category_id` → `gst_categories.id`.
- **Important fields:** `line_number`, `medicine_name_snapshot`, `batch_number_snapshot`, `expiry_snapshot`, `quantity`, `free_quantity`, `unit_cost`, `discount_rate`, `discount_amount`, `tax_rate_snapshot`, `tax_amount`, `line_total`.
- **Relationships:** Belongs to one purchase and one batch; may be referenced by purchase return items.
- **Suggested indexes:** Unique `(purchase_id, line_number)`; `medicine_batch_id`; `medicine_id`.

### `sales`

- **Purpose:** Retail sale invoice header.
- **Primary key:** `id`.
- **Foreign keys:** Optional `customer_id` → `customers.id`; `created_by_user_id` → `users.id`.
- **Important fields:** `invoice_number`, `sale_date`, `status`, `payment_status`, `subtotal`, `discount_total`, `tax_total`, `rounding_amount`, `grand_total`, `notes`.
- **Relationships:** A sale has many sale items and may have many sale returns; customer association is optional.
- **Suggested indexes:** Unique `invoice_number`; `(customer_id, sale_date)`; `(status, sale_date)`; `(created_by_user_id, sale_date)`.

### `sale_items`

- **Purpose:** Batch-specific sale invoice line.
- **Primary key:** `id`.
- **Foreign keys:** `sale_id` → `sales.id`; `medicine_id` → `medicines.id`; `medicine_batch_id` → `medicine_batches.id`; `gst_category_id` → `gst_categories.id`.
- **Important fields:** `line_number`, `medicine_name_snapshot`, `batch_number_snapshot`, `expiry_snapshot`, `quantity`, `unit_price`, `discount_rate`, `discount_amount`, `tax_rate_snapshot`, `tax_amount`, `line_total`.
- **Relationships:** Belongs to one sale and one batch; may be referenced by sale return items.
- **Suggested indexes:** Unique `(sale_id, line_number)`; `medicine_batch_id`; `medicine_id`.

### `purchase_returns`

- **Purpose:** Supplier-return document header associated with an original purchase.
- **Primary key:** `id`.
- **Foreign keys:** `purchase_id` → `purchases.id`; `supplier_id` → `suppliers.id`; `created_by_user_id` → `users.id`.
- **Important fields:** `return_number`, `return_date`, `reason`, `status`, `subtotal`, `tax_total`, `grand_total`.
- **Relationships:** A purchase can have many purchase returns; a purchase return has many items.
- **Suggested indexes:** Unique `return_number`; `(purchase_id, return_date)`; `(supplier_id, return_date)`.

### `purchase_return_items`

- **Purpose:** Batch-specific purchase-return line.
- **Primary key:** `id`.
- **Foreign keys:** `purchase_return_id` → `purchase_returns.id`; `purchase_item_id` → `purchase_items.id`; `medicine_batch_id` → `medicine_batches.id`.
- **Important fields:** `line_number`, `quantity`, `unit_cost_snapshot`, `tax_rate_snapshot`, `tax_amount`, `line_total`, `reason`.
- **Relationships:** Belongs to one return, original purchase item, and batch.
- **Suggested indexes:** Unique `(purchase_return_id, line_number)`; `purchase_item_id`; `medicine_batch_id`.

### `sale_returns`

- **Purpose:** Customer-return document header associated with an original sale.
- **Primary key:** `id`.
- **Foreign keys:** `sale_id` → `sales.id`; optional `customer_id` → `customers.id`; `created_by_user_id` → `users.id`.
- **Important fields:** `return_number`, `return_date`, `reason`, `status`, `subtotal`, `tax_total`, `grand_total`.
- **Relationships:** A sale can have many sale returns; a sale return has many items.
- **Suggested indexes:** Unique `return_number`; `(sale_id, return_date)`; `(customer_id, return_date)`.

### `sale_return_items`

- **Purpose:** Batch-specific sale-return line.
- **Primary key:** `id`.
- **Foreign keys:** `sale_return_id` → `sale_returns.id`; `sale_item_id` → `sale_items.id`; `medicine_batch_id` → `medicine_batches.id`.
- **Important fields:** `line_number`, `quantity`, `unit_price_snapshot`, `tax_rate_snapshot`, `tax_amount`, `line_total`, `reason`, `restock_disposition`.
- **Relationships:** Belongs to one return, original sale item, and batch.
- **Suggested indexes:** Unique `(sale_return_id, line_number)`; `sale_item_id`; `medicine_batch_id`.

### `stock_movements`

- **Purpose:** Immutable per-batch stock ledger.
- **Primary key:** `id`.
- **Foreign keys:** `medicine_id` → `medicines.id`; `medicine_batch_id` → `medicine_batches.id`; optional `performed_by_user_id` → `users.id`.
- **Important fields:** `movement_type`, `quantity_delta`, `occurred_at`, `source_document_type`, `source_document_id`, `reference_number`, `reason`, `recorded_at`.
- **Relationships:** Many movements belong to one medicine and one batch; source document references are polymorphic to purchase, sale, return, or adjustment document classes.
- **Suggested indexes:** `(medicine_batch_id, occurred_at)`; `(medicine_id, occurred_at)`; `(source_document_type, source_document_id)`; `(movement_type, occurred_at)`.

### `inventory`

- **Purpose:** Current per-batch stock projection used for availability and stock status.
- **Primary key:** `id`.
- **Foreign keys:** `medicine_id` → `medicines.id`; `medicine_batch_id` → `medicine_batches.id`.
- **Important fields:** `quantity_on_hand`, `quantity_reserved`, `quantity_available`, `last_movement_at`, `updated_at`.
- **Relationships:** One inventory projection belongs to one batch; the medicine reference supports efficient product-level lookup.
- **Suggested indexes:** Unique `medicine_batch_id`; `(medicine_id, quantity_available)`; `last_movement_at`.

### `audit_logs`

- **Purpose:** Append-only audit history for governed state changes and sensitive events.
- **Primary key:** `id`.
- **Foreign keys:** Optional `actor_user_id` → `users.id`.
- **Important fields:** `occurred_at`, `action`, `target_entity_type`, `target_entity_id`, `before_state`, `after_state`, `request_id`, `source_context`, `ip_address`.
- **Relationships:** An audit entry optionally belongs to one actor user and identifies a target through a typed reference.
- **Suggested indexes:** `(target_entity_type, target_entity_id, occurred_at)`; `(actor_user_id, occurred_at)`; `(action, occurred_at)`; `request_id`.

## Referential and retention notes

- Transaction lines, stock movements, and audit logs are retained for historical traceability; referenced master data should be inactivated, not removed.
- Polymorphic source and audit targets require application-level reference validation in the future design; the reference is indexed for lookup.
- Primary, unique, and foreign-key constraints should be complemented by transaction boundaries when implementation begins. This document intentionally defines no implementation mechanism.
