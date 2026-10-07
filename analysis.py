"""Pure historical performance and cash-flow calculations."""
import math
import pandas as pd


def metrics(prices):
    prices = prices.dropna().sort_index()
    if len(prices) < 2 or (prices <= 0).any():
        raise ValueError("Need at least two positive prices.")
    days = (prices.index[-1] - prices.index[0]).days
    if days <= 0:
        raise ValueError("Prices must cover distinct dates.")
    total = prices.iloc[-1] / prices.iloc[0] - 1
    cagr = (1 + total) ** (365.25 / days) - 1
    volatility = prices.pct_change().dropna().std() * math.sqrt(252)
    drawdown = (prices / prices.cummax() - 1).min()
    return total, cagr, volatility, drawdown


def project(amount, monthly, rate, start, end):
    if amount < 0 or monthly < 0 or rate <= -1 or end < start:
        raise ValueError("Invalid projection inputs.")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    dates = [start]
    n = 1
    while start + pd.DateOffset(months=n) <= end:
        dates.append(start + pd.DateOffset(months=n))
        n += 1
    anniversaries = set(dates[1:])
    if dates[-1] != end:
        dates.append(end)
    value, contributed = float(amount), float(amount)
    rows = [{"Date": start, "Projected value": value, "Contributed": contributed}]
    previous = start
    for current in dates[1:]:
        value *= (1 + rate) ** ((current - previous).days / 365.25)
        if current in anniversaries:
            value += monthly
            contributed += monthly
        rows.append({"Date": current, "Projected value": value, "Contributed": contributed})
        previous = current
    return pd.DataFrame(rows)
