"""Domain exceptions for the Medicine bounded context.

Every exception here is raised from inside an entity or value object to
protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns (no HTTP status codes, no ORM
error wrapping) — translating a domain error into a UI message or an
API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class MedicineDomainError(Exception):
    """Base class for every error raised by the Medicine domain."""


class InvalidMedicineNameError(MedicineDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid medicine name {value!r}: {reason}")


class InvalidGenericNameError(MedicineDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid generic name {value!r}: {reason}")


class InvalidCompositionError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid composition: {reason}")


class InvalidHSNCodeError(MedicineDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid HSN code {value!r}: {reason}")


class InvalidBarcodeError(MedicineDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid barcode {value!r}: {reason}")


class DuplicateBarcodeError(MedicineDomainError):
    def __init__(self, medicine_id: UUID, barcode: str) -> None:
        self.medicine_id = medicine_id
        self.barcode = barcode
        super().__init__(
            f"Medicine {medicine_id} already has barcode {barcode!r} registered"
        )


class BarcodeNotFoundError(MedicineDomainError):
    def __init__(self, medicine_id: UUID, barcode: str) -> None:
        self.medicine_id = medicine_id
        self.barcode = barcode
        super().__init__(
            f"Barcode {barcode!r} is not registered against medicine {medicine_id}"
        )


class InvalidPackConfigurationError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid pack configuration: {reason}")


class InvalidStorageConditionError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid storage condition: {reason}")


class InvalidManufacturerReferenceError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid manufacturer reference: {reason}")


class MedicineAlreadyDiscontinuedError(MedicineDomainError):
    def __init__(self, medicine_id: UUID) -> None:
        self.medicine_id = medicine_id
        super().__init__(f"Medicine {medicine_id} is already discontinued")


class MedicineAlreadyBannedError(MedicineDomainError):
    def __init__(self, medicine_id: UUID) -> None:
        self.medicine_id = medicine_id
        super().__init__(f"Medicine {medicine_id} is banned and cannot be modified")


class MedicineNotActiveError(MedicineDomainError):
    def __init__(self, medicine_id: UUID, current_status: str, action: str) -> None:
        self.medicine_id = medicine_id
        self.current_status = current_status
        self.action = action
        super().__init__(
            f"Cannot {action} medicine {medicine_id}: current status is "
            f"{current_status}"
        )


class TooManyBarcodesError(MedicineDomainError):
    """Raised when a medicine would exceed its maximum registered barcodes.

    Barcode Recognition / OCR integrations are expected to call
    `add_barcode` from automated pipelines; this cap stops a
    misbehaving integration from silently accumulating unbounded junk
    on a product master record.
    """

    def __init__(self, medicine_id: UUID, limit: int) -> None:
        self.medicine_id = medicine_id
        self.limit = limit
        super().__init__(
            f"Medicine {medicine_id} already has the maximum of {limit} "
            "registered barcodes"
        )


class TooManyAlternateNamesError(MedicineDomainError):
    """Raised when a medicine would exceed its maximum alternate names.

    Same rationale as TooManyBarcodesError, but for OCR/AI Vision text
    extraction feeding `add_alternate_name`.
    """

    def __init__(self, medicine_id: UUID, limit: int) -> None:
        self.medicine_id = medicine_id
        self.limit = limit
        super().__init__(
            f"Medicine {medicine_id} already has the maximum of {limit} "
            "alternate names"
        )


class InvalidBatchNumberError(MedicineDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid batch number {value!r}: {reason}")


class InvalidBatchQuantityError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid batch quantity: {reason}")


class InvalidExpiryDateError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid expiry date: {reason}")


class InvalidManufacturingDateError(MedicineDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid manufacturing date: {reason}")


class BatchExpiredError(MedicineDomainError):
    def __init__(self, batch_id: UUID, expiry_date: str) -> None:
        self.batch_id = batch_id
        self.expiry_date = expiry_date
        super().__init__(f"Batch {batch_id} expired on {expiry_date}")


class BatchQuarantinedError(MedicineDomainError):
    def __init__(self, batch_id: UUID, reason: str) -> None:
        self.batch_id = batch_id
        self.reason = reason
        super().__init__(f"Batch {batch_id} is quarantined: {reason}")


class BatchRecalledError(MedicineDomainError):
    def __init__(self, batch_id: UUID, note: str) -> None:
        self.batch_id = batch_id
        self.note = note
        super().__init__(f"Batch {batch_id} is recalled: {note}")


class InsufficientBatchQuantityError(MedicineDomainError):
    def __init__(self, batch_id: UUID, available: int, requested: int) -> None:
        self.batch_id = batch_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Batch {batch_id} has insufficient quantity: {available} available, "
            f"{requested} requested"
        )

