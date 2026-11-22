"""real_cost.py -- the founder's REAL trading cost (his broker's fee board for US shares and exchange-traded funds, ordinary orders; screenshots of 22 Nov 2026).
One place for the fee rules, so every test can use the same real cost instead of a round assumption.

Per ORDER (a buy or a sell):
    commission                     0
    platform fee                   US$0.99 per order
    settlement fee                 US$0.003 per share, at most 1% of the trade amount
    SEC fee                        0.0000206 x trade amount, at least US$0.01 -- SELLS only
    trading activity fee           0
    audit-trail fee (CAT)          US$0.000003 per share
    consumption tax (GST)          9% of all the fees above
NOT on a fee board, and NOT included here: the gap between the buying and the selling price (the spread), the price moving while the order fills,
and the fee for borrowing a share to sell it short. Tests add a stated allowance for the spread on top of these fees.
Borrowed US dollars cost 4.8% a year (the fee board's second tab); see MARGIN_RATE for how the tests use it.

    python -m src.real_cost table      # what one buy-and-sell costs for US$70,000 at different share prices
"""
from __future__ import annotations
import math

ACCOUNT = 70_000.0      # founder, 22 Nov 2026: the account is kept at US$70,000 (gains taken out, losses topped up), so every trade is sized on US$70,000
PLATFORM, SETTLE_PER_SHARE, SETTLE_CAP, SEC_RATE, SEC_MIN, CAT_PER_SHARE, GST = 0.99, 0.003, 0.01, 0.0000206, 0.01, 0.000003, 0.09
MARGIN_RATE = 0.048      # founder's fee board, second tab (22 Nov 2026): 4.8% a year on borrowed US dollars. Buying with one's own US$70,000 borrows nothing. The fee for BORROWING SHARES to sell short is a
                         # different fee, shown per stock on the broker's short-selling page, not on the fee board; until it is known the tests charge every SHORT position 4.8% a year for the nights it is held, as a stand-in.
SPREAD_BP = {"stock": 2.0, "etf": 10.0}      # ALLOWANCE per order, in basis points of the amount -- an assumption (large US shares at the opening auction; single-stock funds trade wider), not a measurement


def order_fee(price: float, shares: float, sell: bool) -> float:
    """fees in US$ for one order of `shares` at `price`"""
    if not (price > 0 and shares > 0): return 0.0
    amount = price * shares; fee = PLATFORM + min(SETTLE_PER_SHARE * shares, SETTLE_CAP * amount) + CAT_PER_SHARE * shares + (max(SEC_MIN, SEC_RATE * amount) if sell else 0.0)
    return fee * (1 + GST)


def short_carry(amount: float, nights: int) -> float:
    """what holding a SHORT position of `amount` costs for `nights` calendar nights, at the stand-in rate"""
    return amount * MARGIN_RATE * max(0, nights) / 365.0


def round_trip(price_in: float, price_out: float, notional: float = ACCOUNT, short: bool = False) -> tuple[float, float]:
    """whole shares bought with `notional` at price_in and closed at price_out -> (fees in US$, the amount really traded). short=True: sold first, bought back."""
    sh = math.floor(notional / price_in) if price_in > 0 else 0
    if sh <= 0: return 0.0, 0.0
    return order_fee(price_in, sh, sell=short) + order_fee(price_out, sh, sell=not short), sh * price_in


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["table"]); ap.parse_args()
    print(f"One buy and one sell of US${ACCOUNT:,.0f}, ordinary orders, fees of the founder's fee board (spread NOT included):")
    print("  share price | shares | fees US$ | fees in basis points of the amount (100 basis points = 1%)")
    for p in (5, 10, 20, 50, 100, 200, 500, 1000):
        f, amt = round_trip(p, p); print(f"  {p:>10} | {int(amt / p):>6} | {f:>8.2f} | {f / amt * 1e4:>5.1f}")
    print(f"  A SHORT position is also charged {MARGIN_RATE:.1%} a year for the nights it is held (stand-in for the share-borrowing fee): US${short_carry(ACCOUNT, 1):.2f} a night on US${ACCOUNT:,.0f} = {short_carry(ACCOUNT, 1) / ACCOUNT * 1e4:.1f} basis points; a weekend counts three nights.")
    print(f"  Allowance added by the tests for the spread: {SPREAD_BP['stock']:.0f} basis points per order for shares, {SPREAD_BP['etf']:.0f} for single-stock funds (assumptions).")
