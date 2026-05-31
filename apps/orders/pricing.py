"""Pricing engine: base + print + color + shipping + tax - discount + commission split."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List
from django.conf import settings

D = Decimal


@dataclass
class LineInput:
    base_price: Decimal
    print_cost: Decimal
    color_extra: Decimal
    quantity: int


@dataclass
class PricingResult:
    subtotal: Decimal
    print_cost_total: Decimal
    color_charges: Decimal
    shipping: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    commission_percent: Decimal
    commission_amount: Decimal
    vendor_payout: Decimal
    line_totals: List[Decimal] = field(default_factory=list)


def calculate_shipping(subtotal: Decimal) -> Decimal:
    return D("0") if subtotal >= D("999") else D("50")


def calculate_tax(taxable: Decimal, rate: Decimal = D("0.05")) -> Decimal:
    return (taxable * rate).quantize(D("0.01"))


def apply_coupon(subtotal: Decimal, coupon) -> Decimal:
    if not coupon or not coupon.is_active:
        return D("0")
    if subtotal < coupon.min_subtotal:
        return D("0")
    if coupon.type == "flat":
        discount = coupon.value
    else:
        discount = (subtotal * coupon.value / D("100"))
    if coupon.max_discount:
        discount = min(discount, coupon.max_discount)
    return discount.quantize(D("0.01"))


def compute(lines: List[LineInput], coupon=None, commission_percent: Decimal = None) -> PricingResult:
    commission_percent = commission_percent or D(str(settings.DEFAULT_COMMISSION_PERCENT))
    subtotal = D("0")
    print_total = D("0")
    color_total = D("0")
    line_totals = []
    for ln in lines:
        line_subtotal = (ln.base_price + ln.color_extra) * ln.quantity
        print_total += ln.print_cost * ln.quantity
        color_total += ln.color_extra * ln.quantity
        subtotal += line_subtotal
        line_totals.append((line_subtotal + ln.print_cost * ln.quantity).quantize(D("0.01")))

    pre_discount = subtotal + print_total
    discount = apply_coupon(pre_discount, coupon)
    shipping = calculate_shipping(pre_discount - discount)
    taxable = pre_discount - discount + shipping
    tax = calculate_tax(taxable)
    total = (taxable + tax).quantize(D("0.01"))

    commission_amount = (total * commission_percent / D("100")).quantize(D("0.01"))
    vendor_payout = (total - commission_amount).quantize(D("0.01"))

    return PricingResult(
        subtotal=subtotal.quantize(D("0.01")),
        print_cost_total=print_total.quantize(D("0.01")),
        color_charges=color_total.quantize(D("0.01")),
        shipping=shipping.quantize(D("0.01")),
        tax=tax,
        discount=discount,
        total=total,
        commission_percent=commission_percent,
        commission_amount=commission_amount,
        vendor_payout=vendor_payout,
        line_totals=line_totals,
    )

