"""Immutable value objects owned by the Medicine bounded context.

Validation and normalisation rules live here so the aggregate never accepts
primitive strings for regulated product-master data. These types deliberately
depend on no database, UI framework, or other bounded context.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from .enums import BarcodeType, StrengthUnit, UnitOfMeasure
from .exceptions import (
    InvalidBarcodeError,
    InvalidBatchNumberError,
    InvalidBatchQuantityError,
    InvalidCompositionError,
    InvalidExpiryDateError,
    InvalidGenericNameError,
    InvalidHSNCodeError,
    InvalidManufacturerReferenceError,
    InvalidManufacturingDateError,
    InvalidMedicineNameError,
    InvalidPackConfigurationError,
    InvalidStorageConditionError,
)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class MedicineId:
    """Stable identity of a medicine aggregate."""

    value: UUID

    @classmethod
    def generate(cls) -> "MedicineId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "MedicineId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class MedicineName:
    """A human-readable medicine brand or product name."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidMedicineNameError(self.value, "a name is required")
        if len(cleaned) > 200:
            raise InvalidMedicineNameError(self.value, "must be at most 200 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class GenericName:
    """The non-proprietary name under which a medicine is classified."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidGenericNameError(self.value, "a generic name is required")
        if len(cleaned) > 200:
            raise InvalidGenericNameError(
                self.value, "must be at most 200 characters"
            )
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CompositionItem:
    """One active ingredient and its strength in a medicine composition."""

    ingredient: str
    strength: Decimal
    unit: StrengthUnit

    def __post_init__(self) -> None:
        ingredient = _normalise_text(self.ingredient)
        if not ingredient:
            raise InvalidCompositionError("each composition item needs an ingredient")
        if len(ingredient) > 200:
            raise InvalidCompositionError("ingredient names must be at most 200 characters")
        if not isinstance(self.strength, Decimal):
            raise InvalidCompositionError("strength must be a Decimal")
        if not self.strength.is_finite() or self.strength <= Decimal("0"):
            raise InvalidCompositionError("strength must be a finite positive value")
        object.__setattr__(self, "ingredient", ingredient)


@dataclass(frozen=True, slots=True)
class Composition:
    """A non-empty, de-duplicated list of active ingredients."""

    items: tuple[CompositionItem, ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise InvalidCompositionError("at least one active ingredient is required")
        normalized_ingredients = [item.ingredient.casefold() for item in self.items]
        if len(set(normalized_ingredients)) != len(normalized_ingredients):
            raise InvalidCompositionError("an ingredient may occur only once")

    @classmethod
    def of(cls, *items: CompositionItem) -> "Composition":
        return cls(items)


@dataclass(frozen=True, slots=True)
class ManufacturerRef:
    """A supplier-independent manufacturer reference on product master data."""

    name: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.name)
        if not cleaned:
            raise InvalidManufacturerReferenceError("a manufacturer name is required")
        if len(cleaned) > 200:
            raise InvalidManufacturerReferenceError(
                "a manufacturer name must be at most 200 characters"
            )
        object.__setattr__(self, "name", cleaned)


@dataclass(frozen=True, slots=True)
class HSNCode:
    """Indian HSN product-classification code represented without punctuation."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip()
        if not cleaned.isdigit() or len(cleaned) not in {4, 6, 8}:
            raise InvalidHSNCodeError(
                self.value, "must contain exactly 4, 6, or 8 digits"
            )
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PackConfiguration:
    """The number of base dispensing units contained in a saleable pack."""

    units_per_pack: int
    unit_of_measure: UnitOfMeasure

    def __post_init__(self) -> None:
        if isinstance(self.units_per_pack, bool) or self.units_per_pack <= 0:
            raise InvalidPackConfigurationError("units per pack must be a positive integer")


@dataclass(frozen=True, slots=True)
class Barcode:
    """A barcode and its declared symbology.

    Check-digit verification is an adapter concern; the domain validates only
    the representation it owns.
    """

    value: str
    barcode_type: BarcodeType = BarcodeType.EAN_13

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split())
        if not cleaned:
            raise InvalidBarcodeError(self.value, "a barcode value is required")
        if len(cleaned) > 128:
            raise InvalidBarcodeError(self.value, "must be at most 128 characters")
        digit_only_types = {
            BarcodeType.EAN_13,
            BarcodeType.EAN_8,
            BarcodeType.UPC_A,
            BarcodeType.UPC_E,
            BarcodeType.ITF_14,
        }
        if self.barcode_type in digit_only_types and not cleaned.isdigit():
            raise InvalidBarcodeError(self.value, "this barcode type must contain digits only")
        expected_lengths = {
            BarcodeType.EAN_13: 13,
            BarcodeType.EAN_8: 8,
            BarcodeType.UPC_A: 12,
            BarcodeType.UPC_E: 8,
            BarcodeType.ITF_14: 14,
        }
        expected_length = expected_lengths.get(self.barcode_type)
        if expected_length is not None and len(cleaned) != expected_length:
            raise InvalidBarcodeError(
                self.value,
                f"{self.barcode_type.value} values must contain {expected_length} digits",
            )
        object.__setattr__(self, "value", cleaned)


@dataclass(frozen=True, slots=True)
class StorageCondition:
    """A concise label for a product's permanent storage requirement."""

    description: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.description)
        if not cleaned:
            raise InvalidStorageConditionError("a storage-condition description is required")
        if len(cleaned) > 250:
            raise InvalidStorageConditionError(
                "a storage-condition description must be at most 250 characters"
            )
        object.__setattr__(self, "description", cleaned)


@dataclass(frozen=True, slots=True)
class MedicineBatchId:
    """Stable identity of a medicine batch entity."""

    value: UUID

    @classmethod
    def generate(cls) -> "MedicineBatchId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "MedicineBatchId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BatchNumber:
    """A manufacturer-assigned batch or lot identifier."""

    value: str

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split())
        if not cleaned:
            raise InvalidBatchNumberError(self.value, "a batch number is required")
        if len(cleaned) > 100:
            raise InvalidBatchNumberError(
                self.value, "must be at most 100 characters"
            )
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class BatchQuantity:
    """Quantity of units in a batch."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or self.value < 0:
            raise InvalidBatchQuantityError("quantity must be a non-negative integer")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ManufacturingDate:
    """Manufacturing date of a batch."""

    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date):
            raise InvalidManufacturingDateError("manufacturing date must be a valid date")

    def __str__(self) -> str:
        return self.value.isoformat()


@dataclass(frozen=True, slots=True)
class ExpiryDate:
    """Expiry date of a batch."""

    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date):
            raise InvalidExpiryDateError("expiry date must be a valid date")

    def __str__(self) -> str:
        return self.value.isoformat()


@dataclass(frozen=True, slots=True)
class ReceivedDate:
    """Date when a batch was received into pharmacy inventory."""

    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date):
            raise InvalidExpiryDateError("received date must be a valid date")

    def __str__(self) -> str:
        return self.value.isoformat()

