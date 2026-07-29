---
name: currency
track: core
kind: deterministic
requires_env: []
inputs: [amount, from_currency, to_currency]
outputs: [result, converted_amount, rate]
side_effect: false
---
# currency

Converts an amount from one currency to another using deterministic exchange rates.
