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
    """Return the cart subtotal in cents.

    BUG: this currently ignores ``quantity``. The demo issue asks Revka to
    add the missing regression test and fix the calculation.
    """

    return sum(item.unit_price_cents for item in items)


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

