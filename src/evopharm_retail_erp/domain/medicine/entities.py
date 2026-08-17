"""Entities for the Medicine bounded context.

Following DDD principles, Medicine is the Aggregate Root. All modifications
to the product master data or its physical batches (Child Entities) must
be coordinated through the Medicine aggregate to guarantee business invariants.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from .enums import BatchSource, BatchStatus, QuarantineReason, StockAdjustmentReason
from .exceptions import (
    BarcodeNotFoundError,
    DuplicateBarcodeError,
    MedicineAlreadyBannedError,
    MedicineAlreadyDiscontinuedError,
    MedicineDomainError,
    MedicineNotActiveError,
    TooManyAlternateNamesError,
    TooManyBarcodesError,
)
from .value_objects import (
    Barcode,
    BatchNumber,
    BatchQuantity,
    Composition,
    ExpiryDate,
    GenericName,
    HSNCode,
    ManufacturingDate,
    ManufacturerRef,
    MedicineBatchId,
    MedicineId,
    MedicineName,
    PackConfiguration,
    ReceivedDate,
    StorageCondition,
)

MEDICINE_STATUS_ACTIVE = "ACTIVE"
MEDICINE_STATUS_DISCONTINUED = "DISCONTINUED"
MEDICINE_STATUS_BANNED = "BANNED"


@dataclass(slots=True, eq=False)
class MedicineBatch:
    """Child entity representing one physical batch of a medicine."""

    id: MedicineBatchId
    batch_number: BatchNumber
    manufacturing_date: ManufacturingDate
    expiry_date: ExpiryDate
    received_date: ReceivedDate
    quantity: BatchQuantity
    source: BatchSource
    status: BatchStatus = BatchStatus.ACTIVE
    quarantine_reason: QuarantineReason | None = None
    adjustment_reason: StockAdjustmentReason | None = None
    recall_note: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MedicineBatch):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- convenience properties -----------------------------------------

    @property
    def is_sellable(self) -> bool:
        """Indicates if the batch is in a status allowing sales."""
        return self.status == BatchStatus.ACTIVE

    @property
    def is_available(self) -> bool:
        """Indicates if the batch is sellable and physically has stock."""
        return self.is_sellable and self.quantity.value > 0

    @property
    def is_terminal(self) -> bool:
        """Indicates if the batch has reached an irreversible end-of-life state."""
        return self.status in (BatchStatus.EXPIRED, BatchStatus.RECALLED, BatchStatus.CONSUMED)

    # -- internals ------------------------------------------------------

    def _update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    # -- lifecycle & state transitions ----------------------------------

    def activate(self) -> None:
        """Make a quarantined batch active again."""
        if self.is_sellable:
            return
        if self.status != BatchStatus.QUARANTINED:
            raise MedicineDomainError(f"Cannot activate batch from status {self.status.value}")
        self.status = BatchStatus.ACTIVE
        self.quarantine_reason = None
        self._update_timestamp()

    def quarantine(self, reason: QuarantineReason) -> None:
        """Place batch under quarantine pending investigation."""
        if not self.is_sellable:
            raise MedicineDomainError(f"Cannot quarantine batch from status {self.status.value}")
        self.status = BatchStatus.QUARANTINED
        self.quarantine_reason = reason
        self._update_timestamp()

    def recall(self, note: str) -> None:
        """Permanently recall the batch."""
        if self.status == BatchStatus.RECALLED:
            return
        if self.status == BatchStatus.CONSUMED:
            raise MedicineDomainError("Cannot recall a consumed batch")
        self.status = BatchStatus.RECALLED
        self.recall_note = note.strip() or None
        self._update_timestamp()

    def mark_expired(self, reference_date: date) -> None:
        """Mark batch as expired if past the expiry date."""
        if self.status == BatchStatus.EXPIRED:
            return
        if self.status in (BatchStatus.RECALLED, BatchStatus.CONSUMED):
            raise MedicineDomainError(f"Cannot mark {self.status.value} batch as expired")
        if self.expiry_date.value > reference_date:
            raise MedicineDomainError("Batch has not expired yet based on the reference date")
        self.status = BatchStatus.EXPIRED
        self._update_timestamp()

    # -- stock movement -------------------------------------------------

    def add_stock(self, quantity: BatchQuantity) -> None:
        """Add stock to this batch."""
        if self.is_terminal:
            raise MedicineDomainError(f"Cannot add stock to batch in terminal status {self.status.value}")
        self.quantity = self.quantity.add(quantity.value)
        self._update_timestamp()

    def deduct_stock(self, quantity: BatchQuantity) -> None:
        """Deduct stock from this batch."""
        if self.is_terminal:
            raise MedicineDomainError(f"Cannot deduct stock from batch in terminal status {self.status.value}")
        self.quantity = self.quantity.subtract(quantity.value)
        if self.quantity.value == 0:
            self.status = BatchStatus.CONSUMED
        self._update_timestamp()

    def adjust_stock(
        self,
        quantity: BatchQuantity,
        reason: StockAdjustmentReason,
        is_deduction: bool = False
    ) -> None:
        """Adjust stock for non-sale reasons (theft, damage, physical counts)."""
        if self.is_terminal:
            raise MedicineDomainError(f"Cannot adjust stock for batch in terminal status {self.status.value}")

        if is_deduction:
            self.quantity = self.quantity.subtract(quantity.value)
        else:
            self.quantity = self.quantity.add(quantity.value)

        self.adjustment_reason = reason
        if self.quantity.value == 0:
            self.status = BatchStatus.CONSUMED
        elif self.status == BatchStatus.CONSUMED and self.quantity.value > 0:
            self.status = BatchStatus.ACTIVE
        self._update_timestamp()


from .enums import (
    BatchSource,
    BatchStatus,
    DosageForm,
    DrugSchedule,
    MedicineStatus,
    QuarantineReason,
    StockAdjustmentReason,
)


@dataclass(slots=True, eq=False)
class Medicine:
    """Aggregate root representing a Medicine product and its physical batches."""

    id: MedicineId
    name: MedicineName
    generic_name: GenericName
    composition: Composition
    manufacturer: ManufacturerRef
    hsn_code: HSNCode
    pack_configuration: PackConfiguration
    storage_condition: StorageCondition | None = None
    dosage_form: DosageForm = DosageForm.TABLET
    schedule: DrugSchedule = DrugSchedule.UNSCHEDULED
    status: MedicineStatus = MedicineStatus.ACTIVE
    _barcodes: set[Barcode] = field(default_factory=set)
    _alternate_names: list[str] = field(default_factory=list)
    _batches: dict[str, MedicineBatch] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    # -- identity ---------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Medicine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- factory ------------------------------------------------------

    @classmethod
    def register(
        cls,
        name: MedicineName,
        generic_name: GenericName,
        composition: Composition,
        manufacturer: ManufacturerRef,
        hsn_code: HSNCode,
        pack_configuration: PackConfiguration,
        dosage_form: DosageForm = DosageForm.TABLET,
        schedule: DrugSchedule = DrugSchedule.UNSCHEDULED,
        barcodes: tuple[Barcode, ...] = (),
        alternate_names: tuple[str, ...] = (),
        storage_condition: StorageCondition | None = None,
        id: MedicineId | None = None,
    ) -> "Medicine":
        """Register a new medicine master record."""
        med_id = id if id is not None else MedicineId.generate()
        clean_alternates: list[str] = []
        for alt in alternate_names:
            c = " ".join(alt.split())
            if c and c.casefold() not in {a.casefold() for a in clean_alternates}:
                clean_alternates.append(c)
        medicine = cls(
            id=med_id,
            name=name,
            generic_name=generic_name,
            composition=composition,
            manufacturer=manufacturer,
            hsn_code=hsn_code,
            pack_configuration=pack_configuration,
            dosage_form=dosage_form,
            schedule=schedule,
            storage_condition=storage_condition,
            _barcodes=set(barcodes),
            _alternate_names=clean_alternates,
        )
        return medicine

    def has_barcode(self, barcode_value: str) -> bool:
        """Check if this medicine has the specified barcode value registered."""
        cleaned = "".join(barcode_value.split())
        return any(bc.value == cleaned for bc in self._barcodes)

    def rename(self, new_name: MedicineName) -> None:
        """Rename the medicine brand name."""
        if self.status == MedicineStatus.BANNED:
            raise MedicineAlreadyBannedError(self.id.value)
        self.name = new_name
        self._touch()

    def mark_under_review(self, reason: str = "") -> None:
        """Place the medicine master record under review."""
        if self.status == MedicineStatus.BANNED:
            raise MedicineAlreadyBannedError(self.id.value)
        self.status = MedicineStatus.UNDER_REVIEW
        self._touch()

    # -- internals ------------------------------------------------------

    def _touch(self) -> None:
        """Bump the optimistic concurrency version and modified timestamp."""
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1

    # -- read-only collections ------------------------------------------

    @property
    def barcodes(self) -> tuple[Barcode, ...]:
        return tuple(self._barcodes)

    @property
    def alternate_names(self) -> tuple[str, ...]:
        return tuple(self._alternate_names)

    @property
    def batches(self) -> tuple[MedicineBatch, ...]:
        return tuple(self._batches.values())

    # -- convenience properties -----------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status == MEDICINE_STATUS_ACTIVE

    @property
    def is_sellable(self) -> bool:
        return self.is_active

    @property
    def is_available(self) -> bool:
        return self.is_active and len(self.available_batches()) > 0

    # -- product lifecycle ----------------------------------------------

    def discontinue(self) -> None:
        if self.status == MEDICINE_STATUS_BANNED:
            raise MedicineAlreadyBannedError(self.id.value)
        if self.status == MEDICINE_STATUS_DISCONTINUED:
            raise MedicineAlreadyDiscontinuedError(self.id.value)
        self.status = MEDICINE_STATUS_DISCONTINUED
        self._touch()
        # TODO: Record MedicineDiscontinuedDomainEvent

    def ban(self) -> None:
        if self.status == MEDICINE_STATUS_BANNED:
            raise MedicineAlreadyBannedError(self.id.value)
        self.status = MEDICINE_STATUS_BANNED
        self._touch()
        # TODO: Record MedicineBannedDomainEvent

    def activate(self) -> None:
        if self.status == MEDICINE_STATUS_BANNED:
            raise MedicineAlreadyBannedError(self.id.value)
        if self.is_active:
            return
        self.status = MEDICINE_STATUS_ACTIVE
        self._touch()
        # TODO: Record MedicineActivatedDomainEvent

    # -- product attributes ---------------------------------------------

    def add_barcode(self, barcode: Barcode, limit: int = 10) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "add barcode")
        if barcode in self._barcodes:
            raise DuplicateBarcodeError(self.id.value, barcode.value)
        if len(self._barcodes) >= limit:
            raise TooManyBarcodesError(self.id.value, limit)

        self._barcodes.add(barcode)
        self._touch()
        # TODO: Record BarcodeAddedDomainEvent

    def remove_barcode(self, barcode: Barcode) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "remove barcode")
        if barcode not in self._barcodes:
            raise BarcodeNotFoundError(self.id.value, barcode.value)

        self._barcodes.remove(barcode)
        self._touch()
        # TODO: Record BarcodeRemovedDomainEvent

    def add_alternate_name(self, name: str, limit: int = 5) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "add alternate name")

        name_clean = " ".join(name.split())
        if not name_clean:
            raise MedicineDomainError("Alternate name cannot be empty")

        if len(self._alternate_names) >= limit:
            raise TooManyAlternateNamesError(self.id.value, limit)

        normalized_existing = {n.casefold() for n in self._alternate_names}
        if name_clean.casefold() not in normalized_existing:
            self._alternate_names.append(name_clean)
            self._touch()
            # TODO: Record AlternateNameAddedDomainEvent

    def remove_alternate_name(self, name: str) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "remove alternate name")

        name_clean = " ".join(name.split())
        target = name_clean.casefold()

        for existing in self._alternate_names:
            if existing.casefold() == target:
                self._alternate_names.remove(existing)
                self._touch()
                # TODO: Record AlternateNameRemovedDomainEvent
                return

        # TODO: Replace with AlternateNameNotFoundError when created
        raise MedicineDomainError(f"Alternate name {name_clean!r} not found")

    # -- batch management -----------------------------------------------

    def get_batch(self, batch_number: BatchNumber) -> MedicineBatch | None:
        return self._batches.get(batch_number.value)

    def receive_batch(
        self,
        batch_id: MedicineBatchId,
        batch_number: BatchNumber,
        manufacturing_date: ManufacturingDate,
        expiry_date: ExpiryDate,
        received_date: ReceivedDate,
        quantity: BatchQuantity,
        source: BatchSource = BatchSource.PURCHASE,
    ) -> MedicineBatch:
        """Receive physical stock of a specific batch."""
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "receive batch")

        if expiry_date.value <= manufacturing_date.value:
            raise MedicineDomainError("Expiry date must be after the manufacturing date")
        if received_date.value < manufacturing_date.value:
            raise MedicineDomainError("Received date cannot be before the manufacturing date")

        existing_batch = self.get_batch(batch_number)
        if existing_batch:
            existing_batch.add_stock(quantity)
            self._touch()
            # TODO: Record BatchStockAddedDomainEvent
            return existing_batch

        new_batch = MedicineBatch(
            id=batch_id,
            batch_number=batch_number,
            manufacturing_date=manufacturing_date,
            expiry_date=expiry_date,
            received_date=received_date,
            quantity=quantity,
            source=source,
        )
        self._batches[batch_number.value] = new_batch
        self._touch()
        # TODO: Record BatchReceivedDomainEvent
        return new_batch

    def activate_batch(self, batch_number: BatchNumber) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "activate batch")
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")

        batch.activate()
        self._touch()
        # TODO: Record BatchActivatedDomainEvent

    def quarantine_batch(self, batch_number: BatchNumber, reason: QuarantineReason) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "quarantine batch")
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")

        batch.quarantine(reason)
        self._touch()
        # TODO: Record BatchQuarantinedDomainEvent

    def recall_batch(self, batch_number: BatchNumber, reason: str) -> None:
        # Recall is permitted even if the product itself has been discontinued
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")

        batch.recall(reason)
        self._touch()
        # TODO: Record BatchRecalledDomainEvent

    def mark_batch_expired(self, batch_number: BatchNumber, reference_date: date) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "mark batch expired")
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")

        batch.mark_expired(reference_date)
        self._touch()
        # TODO: Record BatchExpiredDomainEvent

    def deduct_batch_stock(self, batch_number: BatchNumber, quantity: BatchQuantity) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "deduct stock")
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")
        batch.deduct_stock(quantity)
        self._touch()
        # TODO: Record BatchStockDeductedDomainEvent

    def adjust_batch_stock(
        self,
        batch_number: BatchNumber,
        quantity: BatchQuantity,
        reason: StockAdjustmentReason,
        is_deduction: bool = False
    ) -> None:
        if not self.is_active:
            raise MedicineNotActiveError(self.id.value, self.status, "adjust stock")
        batch = self.get_batch(batch_number)
        if not batch:
            # TODO: Replace with BatchNotFoundError when created
            raise MedicineDomainError(f"Batch {batch_number.value} not found")
        batch.adjust_stock(quantity, reason, is_deduction)
        self._touch()
        # TODO: Record BatchStockAdjustedDomainEvent

    # -- aggregate queries / helpers ------------------------------------

    def available_batches(self) -> tuple[MedicineBatch, ...]:
        """Returns all active batches that have stock > 0."""
        return tuple(
            batch for batch in self._batches.values()
            if batch.is_available
        )

    def next_sellable_batch(self) -> MedicineBatch | None:
        """Returns the available batch with the earliest expiry date (FEFO)."""
        available = self.available_batches()
        if not available:
            return None
        return min(available, key=lambda b: b.expiry_date.value)

    def total_stock(self) -> int:
        """Returns the total sellable stock across all available batches."""
        return sum(batch.quantity.value for batch in self.available_batches())