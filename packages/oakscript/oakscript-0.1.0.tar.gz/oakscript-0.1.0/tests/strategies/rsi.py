from oakscript.pinescript import ta, crossover, crossunder, na
from oakscript.strategytester import Strategy

"""
strategy("RSI Strategy", overlay=true)
length = input( 14 )
overSold = input( 30 )
overBought = input( 70 )
price = close
vrsi = ta.rsi(price, length)
co = ta.crossover(vrsi, overSold)
cu = ta.crossunder(vrsi, overBought)
if (not na(vrsi))
	if (co)
		strategy.entry("RsiLE", strategy.long, comment="RsiLE")
	if (cu)
		strategy.entry("RsiSE", strategy.short, comment="RsiSE")
"""

class RSI_Strategy(Strategy):
    def __init__(self, length=14, overSold=30, overBought=70):
        super().__init__(title="RSI Startegy", shorttitle="RSI Strategy")
        self.length = 14
        self.overSold = 30
        self.overBought = 70

    def next(self):
        prices = self.close

        vrsi = ta.rsi(prices, self.length)
        co = crossover(vrsi, self.overSold)
        cu = crossunder(vrsi, self.overBought)

        if not na(vrsi):
            if co:
                self.strategy.entry("RsiLE", self.strategy.long, comment="RsiLE")
            if cu:
                self.strategy.entry("RsiSE", self.strategy.short, comment="RsiSE")
