from __future__ import annotations

from typing import Any

RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 155.0,
    "VND": 25400.0,
    "SGD": 1.35,
}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict[str, Any]:
    from_curr = str(from_currency).upper().strip()
    to_curr = str(to_currency).upper().strip()

    if from_curr not in RATES or to_curr not in RATES:
        return {
            "error": "unsupported_currency",
            "message": f"Supported currencies: {list(RATES.keys())}",
        }

    usd_amount = float(amount) / RATES[from_curr]
    converted_amount = usd_amount * RATES[to_curr]
    rate = RATES[to_curr] / RATES[from_curr]

    return {
        "amount": amount,
        "from_currency": from_curr,
        "to_currency": to_curr,
        "converted_amount": round(converted_amount, 4),
        "exchange_rate": round(rate, 6),
    }
