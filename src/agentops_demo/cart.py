"""Checkout helpers for a deliberately small cart domain."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


@dataclass(frozen=True)
class LineItem:
    """A line item in a shopping cart."""

    sku: str
    unit_price_cents: int
    quantity: int = 1

    def __post_init__(self) -> None:
        if not self.sku:
            raise ValueError("sku is required")
        if self.unit_price_cents < 0:
            raise ValueError("unit_price_cents must be non-negative")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")


def subtotal_cents(items: Iterable[LineItem]) -> int:
    """Return the cart subtotal in cents."""

    return sum(item.unit_price_cents * item.quantity for item in items)


def round_up_to_nearest(items: Iterable[LineItem], step_cents: int) -> int:
    """Rounds the cart subtotal up to the nearest multiple of step_cents.

    Args:
        items: The line items in the cart.
        step_cents: The multiple to round up to, in cents.

    Returns:
        The subtotal rounded up to the nearest multiple of step_cents.
    """
    if step_cents < 1:
        raise ValueError("step_cents must be at least 1")

    subtotal = subtotal_cents(items)
    if subtotal % step_cents == 0:
        return subtotal
    
    remainder = subtotal % step_cents
    return subtotal + (step_cents - remainder)


def round_subtotal_to_dollars(items: Iterable[LineItem]) -> int:
    """Return the cart subtotal rounded to the nearest dollar, in cents."""

    subtotal = subtotal_cents(items)
    return int(round(subtotal / 100.0) * 100)


def total_with_tax_cents(items: Iterable[LineItem], tax_rate_bps: int) -> int:
    """Return the cart total in cents, including sales tax.

    Args:
        items: The line items in the cart.
        tax_rate_bps: The sales tax rate in basis points (1/100 of 1%).
    """
    if tax_rate_bps < 0:
        raise ValueError("tax_rate_bps must be non-negative")

    subtotal = subtotal_cents(items)
    tax_cents = subtotal * tax_rate_bps / 10000
    return subtotal + round(tax_cents)


def apply_tax(items: Iterable[LineItem], tax_bps: int) -> int:
    """Return subtotal + tax in integer cents, rounded half-up.

    Args:
        items: The line items in the cart.
        tax_bps: The sales tax rate in basis points (1/100 of 1%).
    """
    if tax_bps < 0:
        raise ValueError("tax_bps must be non-negative")

    subtotal = subtotal_cents(items)
    tax = Decimal(subtotal) * (Decimal(tax_bps) / Decimal(10000))
    total = Decimal(subtotal) + tax
    return int(total.to_integral_value(rounding=ROUND_HALF_UP))


def apply_percentage_discount(items: Iterable[LineItem], percent_off: float) -> int:
    """Return the cart subtotal in cents with a percentage discount applied.

    Args:
        items: The line items in the cart.
        percent_off: The discount percentage (e.g., 10 for 10% off).
    """
    if not 0 <= percent_off <= 100:
        raise ValueError("percent_off must be between 0 and 100")

    subtotal = subtotal_cents(items)
    discount_amount = subtotal * (percent_off / 100)
    return round(subtotal - discount_amount)


def apply_flat_discount(items: Iterable[LineItem], discount_cents: int) -> int:
    """Return the cart subtotal minus a flat discount, in cents.

    Args:
        items: The line items in the cart.
        discount_cents: The discount amount in cents.
    """
    subtotal = subtotal_cents(items)
    return max(0, subtotal - discount_cents)


def format_money(cents: int) -> str:
    """Format cents as a US dollar amount."""

    if cents < 0:
        raise ValueError("cents must be non-negative")
    return f"${cents / 100:.2f}"


def receipt_summary(items: Iterable[LineItem]) -> dict[str, int | str]:
    """Return a compact receipt summary for a cart."""

    materialized = list(items)
    subtotal = subtotal_cents(materialized)
    return {
        "line_count": len(materialized),
        "item_count": sum(item.quantity for item in materialized),
        "subtotal_cents": subtotal,
        "subtotal": format_money(subtotal),
    }


def split_evenly(items: Iterable[LineItem], n_ways: int) -> list[int]:
    """Splits the cart subtotal across N people.

    Args:
        items: The line items in the cart.
        n_ways: The number of ways to split the subtotal.

    Returns:
        A list of per-person amounts in integer cents that sum exactly to the
        subtotal.
    """
    if n_ways < 1:
        raise ValueError("n_ways must be at least 1")

    total = subtotal_cents(items)
    base_amount, remainder = divmod(total, n_ways)
    
    amounts = [base_amount] * n_ways
    for i in range(remainder):
        amounts[i] += 1
    
    return amounts
