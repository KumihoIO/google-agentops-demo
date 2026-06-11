"""Checkout helpers for a deliberately small cart domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class LineItem:
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
