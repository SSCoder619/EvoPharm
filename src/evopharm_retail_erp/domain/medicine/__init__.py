"""Medicine domain package.

Public surface of the Medicine bounded context. Only the names
re-exported here are considered stable for other layers (Application,
other domains) to import — internal module layout may be reorganised
freely without breaking callers.
"""
from .entities import Medicine
from .enums import (
    BarcodeType,
    DosageForm,
    DrugSchedule,
    MedicineStatus,
    StrengthUnit,
    UnitOfMeasure,
)
from .exceptions import (
    BarcodeNotFoundError,
    DuplicateBarcodeError,
    InvalidBarcodeError,
    InvalidCompositionError,
    InvalidGenericNameError,
    InvalidHSNCodeError,
    InvalidManufacturerReferenceError,
    InvalidMedicineNameError,
    InvalidPackConfigurationError,
    InvalidStorageConditionError,
    MedicineAlreadyBannedError,
    MedicineAlreadyDiscontinuedError,
    MedicineDomainError,
    MedicineNotActiveError,
    TooManyAlternateNamesError,
    TooManyBarcodesError,
)
from .interfaces import MedicineRepository
from .value_objects import (
    Barcode,
    Composition,
    CompositionItem,
    GenericName,
    HSNCode,
    ManufacturerRef,
    MedicineId,
    MedicineName,
    PackConfiguration,
    StorageCondition,
)

__all__ = [
    "Medicine",
    "MedicineId",
    "MedicineName",
    "GenericName",
    "Composition",
    "CompositionItem",
    "ManufacturerRef",
    "HSNCode",
    "PackConfiguration",
    "Barcode",
    "StorageCondition",
    "DosageForm",
    "UnitOfMeasure",
    "StrengthUnit",
    "DrugSchedule",
    "MedicineStatus",
    "BarcodeType",
    "MedicineRepository",
    "MedicineDomainError",
    "InvalidMedicineNameError",
    "InvalidGenericNameError",
    "InvalidCompositionError",
    "InvalidHSNCodeError",
    "InvalidBarcodeError",
    "DuplicateBarcodeError",
    "BarcodeNotFoundError",
    "InvalidPackConfigurationError",
    "InvalidStorageConditionError",
    "InvalidManufacturerReferenceError",
    "MedicineAlreadyDiscontinuedError",
    "MedicineNotActiveError",
    "MedicineAlreadyBannedError",
    "TooManyBarcodesError",
    "TooManyAlternateNamesError",
]
