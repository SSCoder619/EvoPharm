"""Immutable value objects owned by the Supplier bounded context.

Validation and normalization rules live here so the aggregate root never accepts
invalid GSTIN/PAN compliance IDs, primitive unformatted strings, or bad postal codes.
These types deliberately depend on no database, UI framework, or outer application layer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import (
    InvalidAddressError,
    InvalidEmailAddressError,
    InvalidGSTINError,
    InvalidPANError,
    InvalidPhoneNumberError,
    InvalidSupplierCodeError,
    InvalidSupplierNameError,
)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class SupplierId:
    """Stable identity of a Supplier aggregate root."""

    value: UUID

    @classmethod
    def generate(cls) -> "SupplierId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "SupplierId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class SupplierCode:
    """Unique supplier reference code (e.g. SUP-2026-0001)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidSupplierCodeError(self.value, "supplier code cannot be empty")
        if len(cleaned) > 50:
            raise InvalidSupplierCodeError(self.value, "supplier code must be at most 50 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SupplierName:
    """Supplier legal business name value object."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidSupplierNameError(self.value, "supplier name is required")
        if len(cleaned) < 2:
            raise InvalidSupplierNameError(self.value, "supplier name must be at least 2 characters")
        if len(cleaned) > 200:
            raise InvalidSupplierNameError(self.value, "supplier name must be at most 200 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Contact phone number value object."""

    value: str

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split())
        if not cleaned:
            raise InvalidPhoneNumberError(self.value, "phone number is required")
        digits_only = re.sub(r"[^\d]", "", cleaned)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise InvalidPhoneNumberError(self.value, "must contain between 7 and 15 digits")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """Supplier contact email address value object."""

    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip().lower()
        if not cleaned:
            raise InvalidEmailAddressError(self.value, "email address cannot be empty")
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_pattern, cleaned):
            raise InvalidEmailAddressError(self.value, "invalid email address format")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PostalCode:
    """Postal Code / Indian PIN code value object."""

    value: str

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split())
        if not cleaned:
            raise InvalidAddressError("postal code cannot be empty")
        if not cleaned.isalnum() or len(cleaned) > 12:
            raise InvalidAddressError("postal code must be alphanumeric and up to 12 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Address:
    """Registered office address value object."""

    street: str
    city: str
    state: str
    postal_code: PostalCode
    country: str = "India"

    def __post_init__(self) -> None:
        clean_street = _normalise_text(self.street)
        if not clean_street:
            raise InvalidAddressError("street address is required")
        clean_city = _normalise_text(self.city)
        if not clean_city:
            raise InvalidAddressError("city is required")
        clean_state = _normalise_text(self.state)
        if not clean_state:
            raise InvalidAddressError("state is required")

        object.__setattr__(self, "street", clean_street)
        object.__setattr__(self, "city", clean_city)
        object.__setattr__(self, "state", clean_state)
        object.__setattr__(self, "country", _normalise_text(self.country))

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} - {self.postal_code}, {self.country}"


@dataclass(frozen=True, slots=True)
class GSTIN:
    """Indian Goods and Services Tax Identification Number (15 alphanumeric characters)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split()).upper()
        if not cleaned:
            raise InvalidGSTINError(self.value, "GSTIN cannot be empty")
        gstin_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(gstin_pattern, cleaned):
            raise InvalidGSTINError(
                self.value, "must be a valid 15-character Indian GSTIN (e.g. 29ABCDE1234F1Z5)"
            )
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PAN:
    """Indian Permanent Account Number (10 alphanumeric characters)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = "".join(self.value.split()).upper()
        if not cleaned:
            raise InvalidPANError(self.value, "PAN cannot be empty")
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        if not re.match(pan_pattern, cleaned):
            raise InvalidPANError(
                self.value, "must be a valid 10-character Indian PAN (e.g. ABCDE1234F)"
            )
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
