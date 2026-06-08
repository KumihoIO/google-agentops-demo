"""Run a small sample checkout."""

from __future__ import annotations

import json

from .cart import LineItem, receipt_summary


def main() -> None:
    items = [
        LineItem(sku="notebook", unit_price_cents=1250, quantity=2),
        LineItem(sku="sticker-pack", unit_price_cents=250, quantity=4),
    ]
    print(json.dumps(receipt_summary(items), indent=2))


if __name__ == "__main__":
    main()

