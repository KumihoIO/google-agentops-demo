from agentops_demo import LineItem, format_money, receipt_summary, subtotal_cents


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

