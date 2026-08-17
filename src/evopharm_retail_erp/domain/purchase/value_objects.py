"""Immutable value objects owned by the Purchase bounded context.

Validation and normalization rules live here so the aggregate root and entities
never accept invalid monetary amounts, primitive strings, or negative quantities.
These types deliberately depend on no database, UI framework, or outer application layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

from .exceptions import (
    InvalidInvoiceReferenceError,
    InvalidPurchasePriceError,
    InvalidPurchaseQuantityError,
    InvalidSupplierReferenceError,
)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class PurchaseId:
    """Stable identity of a Purchase aggregate root."""

    value: UUID

    @classmethod
    def generate(cls) -> "PurchaseId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "PurchaseId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class PurchaseLineId:
    """Stable identity of a PurchaseLine child entity."""

    value: UUID

    @classmethod
    def generate(cls) -> "PurchaseLineId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "PurchaseLineId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class SupplierReference:
    """Typed reference to a commercial supplier."""

    supplier_id: UUID
    code: str | None = None
    name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.supplier_id, UUID):
            raise InvalidSupplierReferenceError(self.supplier_id, "supplier_id must be a UUID")
        if self.code is not None:
            clean_code = _normalise_text(self.code)
            if not clean_code:
                raise InvalidSupplierReferenceError(self.code, "supplier code cannot be empty if provided")
            if len(clean_code) > 100:
                raise InvalidSupplierReferenceError(self.code, "supplier code must be at most 100 characters")
            object.__setattr__(self, "code", clean_code)
        if self.name is not None:
            clean_name = _normalise_text(self.name)
            if not clean_name:
                raise InvalidSupplierReferenceError(self.name, "supplier name cannot be empty if provided")
            if len(clean_name) > 200:
                raise InvalidSupplierReferenceError(self.name, "supplier name must be at most 200 characters")
            object.__setattr__(self, "name", clean_name)

    @classmethod
    def of(cls, supplier_id: UUID | str, code: str | None = None, name: str | None = None) -> "SupplierReference":
        sid = UUID(str(supplier_id)) if isinstance(supplier_id, str) else supplier_id
        return cls(supplier_id=sid, code=code, name=name)

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} ({self.supplier_id})"
        return str(self.supplier_id)


@dataclass(frozen=True, slots=True)
class PurchaseOrderReference:
    """Human-readable purchase order reference identifier (e.g. PO-2026-0001)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidSupplierReferenceError(self.value, "purchase order reference cannot be empty")
        if len(cleaned) > 100:
            raise InvalidSupplierReferenceError(self.value, "purchase order reference must be at most 100 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class InvoiceReference:
    """Commercial invoice document reference number."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidInvoiceReferenceError(self.value, "invoice reference cannot be empty")
        if len(cleaned) > 100:
            raise InvalidInvoiceReferenceError(self.value, "invoice reference must be at most 100 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PurchaseQuantity:
    """Integer purchase quantity value object."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidPurchaseQuantityError(self.value, "quantity must be an integer")
        if self.value < 0:
            raise InvalidPurchaseQuantityError(self.value, "quantity cannot be negative")

    @classmethod
    def zero(cls) -> "PurchaseQuantity":
        return cls(0)

    def add(self, amount: int | PurchaseQuantity) -> "PurchaseQuantity":
        add_val = amount.value if isinstance(amount, PurchaseQuantity) else amount
        return PurchaseQuantity(self.value + add_val)

    def subtract(self, amount: int | PurchaseQuantity) -> "PurchaseQuantity":
        sub_val = amount.value if isinstance(amount, PurchaseQuantity) else amount
        if sub_val > self.value:
            raise InvalidPurchaseQuantityError(
                self.value, f"cannot subtract {sub_val} from {self.value}"
            )
        return PurchaseQuantity(self.value - sub_val)

    def is_zero(self) -> bool:
        return self.value == 0

    def is_positive(self) -> bool:
        return self.value > 0

    def __lt__(self, other: object) -> bool:
        if isinstance(other, PurchaseQuantity):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, PurchaseQuantity):
            return self.value <= other.value
        if isinstance(other, int):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, PurchaseQuantity):
            return self.value > other.value
        if isinstance(other, int):
            return self.value > other
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, PurchaseQuantity):
            return self.value >= other.value
        if isinstance(other, int):
            return self.value >= other
        return NotImplemented

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary amount representation using Decimal precision.

    Defaults currency code to 'INR' for Indian Rupee compliance in pharmacy ERP.
    """

    amount: Decimal
    currency: str = "INR"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            if isinstance(self.amount, (int, str)):
                object.__setattr__(self, "amount", Decimal(str(self.amount)))
            else:
                raise InvalidPurchasePriceError(self.amount, "monetary amount must be a Decimal")
        if not self.amount.is_finite():
            raise InvalidPurchasePriceError(self.amount, "monetary amount must be a finite Decimal")
        if self.amount < Decimal("0"):
            raise InvalidPurchasePriceError(self.amount, "monetary amount cannot be negative")
        
        # Normalize to 2 decimal places rounded half up
        quantized = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized)
        object.__setattr__(self, "currency", self.currency.upper().strip())

    @classmethod
    def zero(cls, currency: str = "INR") -> "Money":
        return cls(amount=Decimal("0.00"), currency=currency)

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str = "INR") -> "Money":
        return cls(amount=Decimal(str(amount)), currency=currency)

    def add(self, other: Money) -> "Money":
        self._ensure_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Money) -> "Money":
        self._ensure_same_currency(other)
        if other.amount > self.amount:
            raise InvalidPurchasePriceError(
                self.amount, f"cannot subtract {other.amount} from {self.amount}"
            )
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: int | Decimal) -> "Money":
        mult = Decimal(str(factor))
        if mult < Decimal("0"):
            raise InvalidPurchasePriceError(factor, "multiplier cannot be negative")
        return Money(amount=self.amount * mult, currency=self.currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise InvalidPurchasePriceError(
                other.currency, f"currency mismatch: {self.currency} vs {other.currency}"
            )

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def __add__(self, other: Money) -> Money:
        return self.add(other)

    def __sub__(self, other: Money) -> Money:
        return self.subtract(other)

    def __mul__(self, other: int | Decimal) -> Money:
        return self.multiply(other)

    def __rmul__(self, other: int | Decimal) -> Money:
        return self.multiply(other)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Money):
            self._ensure_same_currency(other)
            return self.amount < other.amount
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Money):
            self._ensure_same_currency(other)
            return self.amount <= other.amount
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Money):
            self._ensure_same_currency(other)
            return self.amount > other.amount
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Money):
            self._ensure_same_currency(other)
            return self.amount >= other.amount
        return NotImplemented

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True, slots=True)
class UnitPrice:
    """Strictly non-negative unit price value object."""

    value: Money

    def __post_init__(self) -> None:
        if not isinstance(self.value, Money):
            raise InvalidPurchasePriceError(self.value, "unit price value must be Money")

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str = "INR") -> "UnitPrice":
        return cls(Money.of(amount, currency))

    @property
    def amount(self) -> Decimal:
        return self.value.amount

    def multiply(self, quantity: int | PurchaseQuantity) -> Money:
        qty_val = quantity.value if isinstance(quantity, PurchaseQuantity) else quantity
        return self.value.multiply(qty_val)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Discount:
    """Discount applied as percentage (0-100%) or fixed monetary amount."""

    percentage: Decimal = Decimal("0.00")
    fixed_amount: Money = field(default_factory=Money.zero)

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Decimal):
            object.__setattr__(self, "percentage", Decimal(str(self.percentage)))
        if self.percentage < Decimal("0.00") or self.percentage > Decimal("100.00"):
            raise InvalidPurchasePriceError(
                self.percentage, "discount percentage must be between 0 and 100"
            )
        if not isinstance(self.fixed_amount, Money):
            raise InvalidPurchasePriceError(self.fixed_amount, "fixed amount must be Money")

    @classmethod
    def none(cls) -> "Discount":
        return cls(percentage=Decimal("0.00"), fixed_amount=Money.zero())

    @classmethod
    def percent(cls, pct: Decimal | int | str) -> "Discount":
        return cls(percentage=Decimal(str(pct)), fixed_amount=Money.zero())

    @classmethod
    def fixed(cls, amount: Money | Decimal | int | str) -> "Discount":
        m_amt = amount if isinstance(amount, Money) else Money.of(amount)
        return cls(percentage=Decimal("0.00"), fixed_amount=m_amt)

    def calculate_discount_amount(self, base_amount: Money) -> Money:
        """Calculate discount amount from percentage and fixed discount."""
        pct_discount = Money(
            amount=base_amount.amount * (self.percentage / Decimal("100.00")),
            currency=base_amount.currency,
        )
        total_disc = pct_discount.add(self.fixed_amount)
        if total_disc.amount > base_amount.amount:
            return base_amount
        return total_disc


@dataclass(frozen=True, slots=True)
class TaxRate:
    """GST / Sales Tax rate percentage (e.g. 5.0, 12.0, 18.0, 28.0)."""

    percentage: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Decimal):
            object.__setattr__(self, "percentage", Decimal(str(self.percentage)))
        if self.percentage < Decimal("0.00") or self.percentage > Decimal("100.00"):
            raise InvalidPurchasePriceError(
                self.percentage, "tax rate percentage must be between 0 and 100"
            )

    @classmethod
    def zero(cls) -> "TaxRate":
        return cls(Decimal("0.00"))

    @classmethod
    def of(cls, pct: Decimal | int | str) -> "TaxRate":
        return cls(Decimal(str(pct)))

    def calculate_tax_amount(self, taxable_amount: Money) -> Money:
        """Calculate tax amount for a given taxable base Money amount."""
        tax_val = taxable_amount.amount * (self.percentage / Decimal("100.00"))
        return Money(amount=tax_val, currency=taxable_amount.currency)

    def __str__(self) -> str:
        return f"{self.percentage:.2f}%"


@dataclass(frozen=True, slots=True)
class PurchaseTotal:
    """Calculated immutable financial total for a Purchase order."""

    subtotal: Money
    total_discount: Money
    taxable_amount: Money
    total_tax: Money
    net_total: Money

    def __post_init__(self) -> None:
        expected_taxable = self.subtotal.subtract(self.total_discount) if self.subtotal >= self.total_discount else Money.zero(self.subtotal.currency)
        if self.taxable_amount != expected_taxable:
            raise InvalidPurchasePriceError(
                self.taxable_amount,
                f"taxable amount {self.taxable_amount} does not match subtotal - discount ({expected_taxable})",
            )
        expected_net = self.taxable_amount.add(self.total_tax)
        if self.net_total != expected_net:
            raise InvalidPurchasePriceError(
                self.net_total,
                f"net total {self.net_total} does not match taxable + tax ({expected_net})",
            )

    @classmethod
    def create(
        cls,
        subtotal: Money,
        total_discount: Money,
        total_tax: Money,
    ) -> "PurchaseTotal":
        taxable = subtotal.subtract(total_discount) if subtotal >= total_discount else Money.zero(subtotal.currency)
        net = taxable.add(total_tax)
        return cls(
            subtotal=subtotal,
            total_discount=total_discount,
            taxable_amount=taxable,
            total_tax=total_tax,
            net_total=net,
        )

    @classmethod
    def zero(cls, currency: str = "INR") -> "PurchaseTotal":
        zero_m = Money.zero(currency)
        return cls(
            subtotal=zero_m,
            total_discount=zero_m,
            taxable_amount=zero_m,
            total_tax=zero_m,
            net_total=zero_m,
        )
