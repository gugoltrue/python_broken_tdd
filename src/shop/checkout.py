"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _validate_line(line: dict[str, str]) -> str | None:
    """Validate a single order line. Return a reason or None if valid."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"Missing key: {key}"
    if not line.get("sku", "").strip():
        return "SKU cannot be empty"
    qty_str = line["qty"]
    stripped = qty_str.lstrip("-+")
    if not stripped.isdigit():
        return "qty must be a whole number"
    if int(qty_str) <= 0:
        return "qty must be greater than zero"
    price_str = line["unit_price_kopecks"]
    if price_str.startswith("-"):
        return "price must not be negative"
    if not price_str.isdigit():
        return "price must be a whole number"
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "Lines cannot be empty"
    if promo_code and promo_code not in PROMO_CODES:
        return "no such promocode exists"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "the city isn't supported"
    for line in lines:
        reason = _validate_line(line)
        if reason:
            return reason
    skus = [line["sku"] for line in lines]
    if len(skus) != len(set(skus)):
        return "the same article may appear only once"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if not lines:
        return None
    subtotal = 0
    total_qty = 0
    for line in lines:
        qty = int(line["qty"])
        unit_price = int(line["unit_price_kopecks"])
        subtotal += qty * unit_price
        total_qty += qty

    tier_discount_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if total_qty >= threshold:
            tier_discount_percent = percent

    promo_percent = PROMO_CODES.get(promo_code, 0)

    discount_percent = max(tier_discount_percent, promo_percent)

    if discount_percent > MAX_DISCOUNT_PERCENT:
        discount_percent = MAX_DISCOUNT_PERCENT

    discount = percent_of(subtotal, discount_percent)

    discounted_subtotal = subtotal - discount

    if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS:
        delivery = SHIPPING_KOPEKS
    else:
        delivery = 0

    base = discounted_subtotal + delivery

    vat = percent_of(base, VAT_PERCENT)

    return base + vat
