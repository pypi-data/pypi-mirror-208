import math
from _decimal import Decimal, ROUND_HALF_UP, ROUND_UP, ROUND_DOWN

import numpy as np
import pandas as pd

mintick = 2  # syminfo.mintick


def add_ticks(price, ticks):
    # FIXME Make the parameter configurable
    global mintick
    return price + get_price_from_ticks(ticks)


def sub_ticks(price, ticks):
    # FIXME Make the parameter configurable
    global mintick
    return max(price - get_price_from_ticks(ticks), 0)


def get_price_from_ticks(ticks):
    return ticks / (10 ** mintick)


def safe_div(n, d):
    return n / d if d else 0


def round_decimal(x, n, rounding_type):
    dec = Decimal(str(x))
    r = Decimal((0, (1,), -n))
    return np.nan if math.isinf(x) else float(dec.quantize(r, rounding=rounding_type))


def roundhalfup(x, n=2):
    return round_decimal(x, n, ROUND_HALF_UP)


def roundup(x, n=2):
    return round_decimal(x, n, ROUND_UP)


def rounddown(x, n=2):
    return round_decimal(x, n, ROUND_DOWN)


def percent(start, end):
    return 100 * (end - start) / start


def is_high_first(bar: pd.Series):
    return bar.high - bar.open < bar.open - bar.low


def is_low_first(bar: pd.Series):
    return bar.high - bar.open > bar.open - bar.low


def marketdata_crossunder(bar, price):
    if is_low_first(bar):
        return (bar.open >= price >= bar.low) or (bar.close <= price <= bar.high)
    if is_high_first(bar):
        return bar.low <= price <= bar.high


def marketdata_crossover(bar, price):
    if is_low_first(bar):
        return bar.low < price < bar.high
    elif is_high_first(bar):
        return (bar.open < price < bar.high) or (bar.low < price < bar.close)


def get_marketdata_range(marketdata, entry_date, exit_date, entry_price, exit_price):
    # FIXME Depending on the type of exit (Take profit, Stoploss, Trail, ...), some prices should be included or not
    marketdata_range = marketdata.loc[exit_date:entry_date].copy()
    entry_bar = marketdata_range.iloc[-1]
    exit_bar = marketdata_range.iloc[0]

    # Case 1: There is high/low on closing bar for an exit price at open
    if exit_price == roundhalfup(exit_bar.open):
        marketdata_range.iloc[0] = [exit_bar.open, exit_bar.open, exit_bar.open, exit_bar.open]
    # elif entry_bar.open == entry_bar.high:
    #    marketdata_range.iloc[0] = [exit_bar.open, exit_bar.high, exit_bar.open, exit_bar.open]
    # Case 2: Limit order close at limit
    else:
        marketdata_range.iloc[0] = [exit_bar.open, exit_price, exit_price, exit_bar.close]
    return marketdata_range
