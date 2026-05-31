from decimal import Decimal
from apps.orders.pricing import LineInput, compute


def test_pricing_basic():
    lines = [LineInput(base_price=Decimal("400"), print_cost=Decimal("100"), color_extra=Decimal("0"), quantity=1)]
    r = compute(lines, commission_percent=Decimal("15"))
    assert r.subtotal == Decimal("400.00")
    assert r.print_cost_total == Decimal("100.00")
    assert r.shipping == Decimal("50.00")
    # tax = 5% of (400+100+50) = 27.5
    assert r.tax == Decimal("27.50")
    assert r.total == Decimal("577.50")
    assert r.commission_amount == (r.total * Decimal("15") / Decimal("100")).quantize(Decimal("0.01"))
    assert r.vendor_payout == (r.total - r.commission_amount).quantize(Decimal("0.01"))


def test_pricing_free_shipping_threshold():
    lines = [LineInput(base_price=Decimal("999"), print_cost=Decimal("100"), color_extra=Decimal("0"), quantity=1)]
    r = compute(lines)
    assert r.shipping == Decimal("0.00")

