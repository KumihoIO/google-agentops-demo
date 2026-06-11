from agentops_demo import (
    LineItem,
    format_money,
    receipt_summary,
    subtotal_cents,
    total_with_tax_cents,
    apply_percentage_discount,
    round_subtotal_to_dollars,
)


def test_subtotal_for_single_quantity_items() -> None:
    items = [
        LineItem(sku="notebook", unit_price_cents=1250),
        LineItem(sku="sticker-pack", unit_price_cents=250),
    ]

    assert subtotal_cents(items) == 1500


def test_receipt_summary_counts_items() -> None:
    summary = receipt_summary(
        [
            LineItem(sku="notebook", unit_price_cents=1250),
            LineItem(sku="sticker-pack", unit_price_cents=250),
        ]
    )

    assert summary == {
        "line_count": 2,
        "item_count": 2,
        "subtotal_cents": 1500,
        "subtotal": "$15.00",
    }


def test_format_money_rejects_negative_values() -> None:
    try:
        format_money(-1)
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_subtotal_respects_quantity() -> None:
    items = [
        LineItem(sku="notebook", unit_price_cents=1250, quantity=3),
        LineItem(sku="sticker-pack", unit_price_cents=250),
    ]
    # 1250*3 + 250*1 = 4000
    assert subtotal_cents(items) == 4000


def test_total_with_tax() -> None:
    items = [
        LineItem(sku="shirt", unit_price_cents=2000, quantity=4),  # 8000
        LineItem(sku="pants", unit_price_cents=2000, quantity=1),  # 2000
    ]
    # subtotal is 10000 cents ($100.00)
    # tax at 8.75% is 875 cents ($8.75)
    assert total_with_tax_cents(items, tax_rate_bps=875) == 10875


def test_apply_percentage_discount() -> None:
    items = [
        LineItem(sku="notebook", unit_price_cents=1000),
        LineItem(sku="pen", unit_price_cents=200),
    ]
    # Subtotal is 1200 cents. 10% off is 120 cents.
    # 1200 - 120 = 1080
    assert apply_percentage_discount(items, 10) == 1080

    # Test with rounding
    items_for_rounding = [
        LineItem(sku="notebook", unit_price_cents=999),
    ]
    # Subtotal is 999. 10% off is 99.9
    # 999 - 99.9 = 899.1 which rounds to 899
    assert apply_percentage_discount(items_for_rounding, 10) == 899


def test_round_subtotal_to_dollars() -> None:
    """Tests rounding of subtotal to the nearest dollar."""
    # $12.49 rounds down to $12.00
    items_round_down = [LineItem(sku="item", unit_price_cents=1249)]
    assert round_subtotal_to_dollars(items_round_down) == 1200

    # $12.50 rounds to nearest even ($12.00)
    items_round_half_even = [LineItem(sku="item", unit_price_cents=1250)]
    assert round_subtotal_to_dollars(items_round_half_even) == 1200

    # $13.50 rounds to nearest even ($14.00)
    items_round_half_odd = [LineItem(sku="item", unit_price_cents=1350)]
    assert round_subtotal_to_dollars(items_round_half_odd) == 1400

    # $12.51 rounds up to $13.00
    items_round_up = [LineItem(sku="item", unit_price_cents=1251)]
    assert round_subtotal_to_dollars(items_round_up) == 1300

    # Test with multiple items, subtotal $12.50, rounds to $12.00
    items_multiple = [
        LineItem(sku="a", unit_price_cents=1020),  # $10.20
        LineItem(sku="b", unit_price_cents=230),  # $2.30
    ]
    assert round_subtotal_to_dollars(items_multiple) == 1200

    # Test with multiple items, subtotal $13.50, rounds to $14.00
    items_multiple_2 = [
        LineItem(sku="a", unit_price_cents=1020),  # $10.20
        LineItem(sku="b", unit_price_cents=330),  # $3.30
    ]
    assert round_subtotal_to_dollars(items_multiple_2) == 1400
