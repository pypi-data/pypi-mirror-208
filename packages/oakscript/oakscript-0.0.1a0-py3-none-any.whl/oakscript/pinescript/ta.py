import talib


def rsi(v, *args):
    return talib.RSI(v[::-1], *args)[::-1]
