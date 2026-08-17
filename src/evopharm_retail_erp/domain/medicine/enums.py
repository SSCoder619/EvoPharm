"""Enum definitions for the Medicine bounded context.

Every enum here is used across entities and value objects to represent a
finite set of valid states or categories. None of them carry any dependency on
infrastructure or presentation concerns (no dynamic value generation, no ORM
mapping logic) — translating enum values into UI labels or API responses is
a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class BatchStatus(str, Enum):
    """Lifecycle status of a medicine batch."""

    ACTIVE = "ACTIVE"
    QUARANTINED = "QUARANTINED"
    EXPIRED = "EXPIRED"
    RECALLED = "RECALLED"
    CONSUMED = "CONSUMED"


@unique
class BatchSource(str, Enum):
    """Origin channel through which a batch entered inventory."""

    PURCHASE = "PURCHASE"
    CUSTOMER_RETURN = "CUSTOMER_RETURN"
    SUPPLIER_REPLACEMENT = "SUPPLIER_REPLACEMENT"
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"
    OPENING_STOCK = "OPENING_STOCK"


@unique
class QuarantineReason(str, Enum):
    """Business justification for placing a batch under quarantine."""

    PENDING_QUALITY_CHECK = "PENDING_QUALITY_CHECK"
    DAMAGED_PACKAGING = "DAMAGED_PACKAGING"
    TEMPERATURE_EXCURSION = "TEMPERATURE_EXCURSION"
    SUSPECTED_COUNTERFEIT = "SUSPECTED_COUNTERFEIT"
    REGULATORY_HOLD = "REGULATORY_HOLD"
    RECALL_INVESTIGATION = "RECALL_INVESTIGATION"


@unique
class StockAdjustmentReason(str, Enum):
    """Business justification for manual inventory adjustments."""

    PHYSICAL_COUNT_VARIANCE = "PHYSICAL_COUNT_VARIANCE"
    DAMAGE = "DAMAGE"
    THEFT_OR_LOSS = "THEFT_OR_LOSS"
    EXPIRY_WRITE_OFF = "EXPIRY_WRITE_OFF"
    CORRECTION = "CORRECTION"


@unique
class MedicineStatus(str, Enum):
    """Lifecycle status of a medicine product master record."""

    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    DISCONTINUED = "DISCONTINUED"
    BANNED = "BANNED"


@unique
class DosageForm(str, Enum):
    """Pharmaceutical dosage form of a medicine product."""

    TABLET = "TABLET"
    CAPSULE = "CAPSULE"
    SYRUP = "SYRUP"
    INJECTION = "INJECTION"
    OINTMENT = "OINTMENT"
    CREAM = "CREAM"
    DROPS = "DROPS"
    INHALER = "INHALER"
    POWDER = "POWDER"
    GEL = "GEL"
    SUSPENSION = "SUSPENSION"
    SOLUTION = "SOLUTION"
    LOTION = "LOTION"


@unique
class DrugSchedule(str, Enum):
    """Indian Drugs and Cosmetics Rules Schedule classification."""

    SCHEDULE_H = "SCHEDULE_H"
    SCHEDULE_H1 = "SCHEDULE_H1"
    SCHEDULE_X = "SCHEDULE_X"
    SCHEDULE_G = "SCHEDULE_G"
    OTC = "OTC"
    GENERAL = "GENERAL"
    UNSCHEDULED = "UNSCHEDULED"


@unique
class UnitOfMeasure(str, Enum):
    """Base dispensing unit of measure for packaging."""

    TABLET = "TABLET"
    CAPSULE = "CAPSULE"
    BOTTLE = "BOTTLE"
    VIAL = "VIAL"
    AMPOULE = "AMPOULE"
    TUBE = "TUBE"
    PACK = "PACK"
    SACHET = "SACHET"
    STRIP = "STRIP"
    PIECE = "PIECE"


@unique
class StrengthUnit(str, Enum):
    """Measurement unit for active ingredient strength."""

    MG = "MG"
    G = "G"
    ML = "ML"
    MCG = "MCG"
    IU = "IU"
    PERCENT = "PERCENT"
    MG_PER_ML = "MG_PER_ML"


@unique
class BarcodeType(str, Enum):
    """Supported barcode symbologies for product identification."""

    EAN_13 = "EAN_13"
    EAN_8 = "EAN_8"
    UPC_A = "UPC_A"
    UPC_E = "UPC_E"
    CODE_128 = "CODE_128"
    CODE_39 = "CODE_39"
    QR_CODE = "QR_CODE"
    DATA_MATRIX = "DATA_MATRIX"
    ITF_14 = "ITF_14"