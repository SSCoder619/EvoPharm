"""Immutable value objects owned by the Invoice bounded context.

Validation and normalization rules live here so the aggregate root and entities
never accept invalid monetary amounts, primitive strings, or negative quantities.
These types deliberately depend on no database, UI framework, or outer application layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4

from .enums import TaxType
from .exceptions import (
    InvalidInvoiceAmountError,
    InvalidInvoiceNumberError,
    InvalidInvoiceQuantityError,
    InvalidTaxRateError,
)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class InvoiceId:
    """Stable identity of an Invoice aggregate root."""

    value: UUID

    @classmethod
    def generate(cls) -> "InvoiceId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "InvoiceId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class InvoiceLineId:
    """Stable identity of an InvoiceLine child entity."""

    value: UUID

    @classmethod
    def generate(cls) -> "InvoiceLineId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "InvoiceLineId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class InvoiceNumber:
    """Commercial retail invoice document number (e.g. INV-2026-00001)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.value)
        if not cleaned:
            raise InvalidInvoiceNumberError(self.value, "invoice number cannot be empty")
        if len(cleaned) > 100:
            raise InvalidInvoiceNumberError(self.value, "invoice number must be at most 100 characters")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SaleReference:
    """Typed reference to a source retail Sale transaction."""

    sale_id: UUID
    sale_invoice_number: str | None = None

    def __str__(self) -> str:
        if self.sale_invoice_number:
            return f"Sale#{self.sale_invoice_number}"
        return f"Sale#{str(self.sale_id)[:8]}"


@dataclass(frozen=True, slots=True)
class CustomerReference:
    """Customer reference information printed on invoice."""

    customer_id: UUID | None = None
    name: str | None = None
    gstin: str | None = None

    def __str__(self) -> str:
        return self.name or "Walk-in Customer"


@dataclass(frozen=True, slots=True)
class InvoiceQuantity:
    """Integer invoice line quantity value object."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidInvoiceQuantityError(self.value, "quantity must be an integer")
        if self.value < 0:
            raise InvalidInvoiceQuantityError(self.value, "quantity cannot be negative")

    @classmethod
    def zero(cls) -> "InvoiceQuantity":
        return cls(0)

    def is_zero(self) -> bool:
        return self.value == 0

    def is_positive(self) -> bool:
        return self.value > 0

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary amount representation using Decimal precision."""

    amount: Decimal
    currency: str = "INR"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            if isinstance(self.amount, (int, str)):
                object.__setattr__(self, "amount", Decimal(str(self.amount)))
            else:
                raise InvalidInvoiceAmountError(self.amount, "monetary amount must be a Decimal")
        if not self.amount.is_finite():
            raise InvalidInvoiceAmountError(self.amount, "monetary amount must be a finite Decimal")
        if self.amount < Decimal("0"):
            raise InvalidInvoiceAmountError(self.amount, "monetary amount cannot be negative")

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
            raise InvalidInvoiceAmountError(
                self.amount, f"cannot subtract {other.amount} from {self.amount}"
            )
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: int | Decimal) -> "Money":
        mult = Decimal(str(factor))
        if mult < Decimal("0"):
            raise InvalidInvoiceAmountError(factor, "multiplier cannot be negative")
        return Money(amount=self.amount * mult, currency=self.currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise InvalidInvoiceAmountError(
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
    """Strictly non-negative selling unit price value object."""

    value: Money

    def __post_init__(self) -> None:
        if not isinstance(self.value, Money):
            raise InvalidInvoiceAmountError(self.value, "unit price value must be Money")

    @classmethod
    def of(cls, amount: Decimal | int | str, currency: str = "INR") -> "UnitPrice":
        return cls(Money.of(amount, currency))

    @property
    def amount(self) -> Decimal:
        return self.value.amount

    def multiply(self, quantity: int | InvoiceQuantity) -> Money:
        qty_val = quantity.value if isinstance(quantity, InvoiceQuantity) else quantity
        return self.value.multiply(qty_val)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class DiscountAmount:
    """Discount applied as percentage or fixed monetary amount."""

    percentage: Decimal = Decimal("0.00")
    fixed_amount: Money = field(default_factory=Money.zero)

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Decimal):
            object.__setattr__(self, "percentage", Decimal(str(self.percentage)))
        if self.percentage < Decimal("0.00") or self.percentage > Decimal("100.00"):
            raise InvalidInvoiceAmountError(
                self.percentage, "discount percentage must be between 0 and 100"
            )
        if not isinstance(self.fixed_amount, Money):
            raise InvalidInvoiceAmountError(self.fixed_amount, "fixed amount must be Money")

    @classmethod
    def none(cls) -> "DiscountAmount":
        return cls(percentage=Decimal("0.00"), fixed_amount=Money.zero())

    @classmethod
    def percent(cls, pct: Decimal | int | str) -> "DiscountAmount":
        return cls(percentage=Decimal(str(pct)), fixed_amount=Money.zero())

    @classmethod
    def fixed(cls, amount: Money | Decimal | int | str) -> "DiscountAmount":
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
    """GST / Sales Tax rate percentage (e.g. 0%, 5%, 12%, 18%, 28%)."""

    percentage: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Decimal):
            object.__setattr__(self, "percentage", Decimal(str(self.percentage)))
        if self.percentage < Decimal("0.00") or self.percentage > Decimal("100.00"):
            raise InvalidTaxRateError(
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
class GstBreakdown:
    """Explicit Indian GST tax breakdown (CGST, SGST, IGST)."""

    tax_type: TaxType
    total_tax: Money
    cgst: Money
    sgst: Money
    igst: Money

    @classmethod
    def calculate(
        cls,
        taxable_amount: Money,
        tax_rate: TaxRate,
        tax_type: TaxType = TaxType.INTRA_STATE,
    ) -> "GstBreakdown":
        """Calculate GST breakdown based on tax rate and place of supply (tax type)."""
        tot_tax = tax_rate.calculate_tax_amount(taxable_amount)
        curr = taxable_amount.currency

        if tax_type == TaxType.INTRA_STATE:
            # 50% CGST + 50% SGST
            half = Money(amount=tot_tax.amount / Decimal("2"), currency=curr)
            return cls(
                tax_type=TaxType.INTRA_STATE,
                total_tax=tot_tax,
                cgst=half,
                sgst=half,
                igst=Money.zero(curr),
            )
        else:
            # 100% IGST
            return cls(
                tax_type=TaxType.INTER_STATE,
                total_tax=tot_tax,
                cgst=Money.zero(curr),
                sgst=Money.zero(curr),
                igst=tot_tax,
            )


@dataclass(frozen=True, slots=True)
class InvoiceTotal:
    """Calculated immutable financial total for an Invoice."""

    subtotal: Money
    total_discount: Money
    taxable_amount: Money
    cgst_amount: Money
    sgst_amount: Money
    igst_amount: Money
    total_tax: Money
    net_total: Money

    @classmethod
    def create(
        cls,
        subtotal: Money,
        total_discount: Money,
        cgst_amount: Money,
        sgst_amount: Money,
        igst_amount: Money,
    ) -> "InvoiceTotal":
        taxable = subtotal.subtract(total_discount) if subtotal >= total_discount else Money.zero(subtotal.currency)
        tot_tax = cgst_amount.add(sgst_amount).add(igst_amount)
        net = taxable.add(tot_tax)
        return cls(
            subtotal=subtotal,
            total_discount=total_discount,
            taxable_amount=taxable,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            total_tax=tot_tax,
            net_total=net,
        )

    @classmethod
    def zero(cls, currency: str = "INR") -> "InvoiceTotal":
        zero_m = Money.zero(currency)
        return cls(
            subtotal=zero_m,
            total_discount=zero_m,
            taxable_amount=zero_m,
            cgst_amount=zero_m,
            sgst_amount=zero_m,
            igst_amount=zero_m,
            total_tax=zero_m,
            net_total=zero_m,
        )
