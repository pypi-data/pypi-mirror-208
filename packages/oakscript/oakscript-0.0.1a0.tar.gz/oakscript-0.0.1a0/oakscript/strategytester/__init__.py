import numpy as np
import pandas as pd

from oakscript.strategytester.reports import process_trades_list, process_performance_summary, rename_columns, \
    filter_columns
from oakscript.util import roundhalfup, rounddown, roundup, add_ticks, sub_ticks, get_price_from_ticks, \
    marketdata_crossover, marketdata_crossunder, is_high_first, is_low_first

trade_num_inc = 0

def get_trade_num():
    global trade_num_inc
    trade_num_inc += 1
    return trade_num_inc


class Order:
    def __init__(self, id: str, direction: str, qty: int, trade_num=None):
        assert direction in ["BUY", "SELL"]
        # assert qty < 0 or qty > 0

        self.trade_num = trade_num or get_trade_num()
        self.direction = direction
        self.contracts = self._get_short_qty(qty) if self.is_short() else qty
        # self.comment = None
        self.entry_price = None
        self.type = None
        self.limit = None  # Both entry and exit order have limit
        self.stop = None  # Both entry and exit order have stop
        self.date_time = None

    def _get_short_qty(self, qty):
        return qty * -1

    def is_entry(self):
        return self.type.startswith("Entry")

    def is_exit(self):
        return self.type.startswith("Exit")

    def is_long(self):
        return self.direction == "BUY"

    def is_short(self):
        return self.direction == 'SELL'

    def _type(self, direction):
        return 'Long' if direction == "BUY" else 'Short'


class EntryOrder(Order):
    def __init__(self, entry_id, direction, qty, trade_num=None):
        assert entry_id
        super().__init__(entry_id, direction, qty, trade_num)
        self.type = 'Entry Long' if self.direction == "BUY" else 'Entry Short'
        # TV attributes
        self.entry_id = entry_id
        self.entry_bar_index = None
        self.entry_comment = None


class ExitOrder(Order):
    def __init__(self, exit_id, direction, qty, trade_num=None):
        assert exit_id
        super().__init__(exit_id, direction, qty, trade_num)
        self.type = 'Exit Short' if self.direction == "BUY" else 'Exit Long'
        self.loss = None
        self.profit = None
        self.trail_hit = False
        self.trail_points = None
        self.trail_price = None

        self.trail_offset = None
        self.trail_offset_price = None
        self.trail_offset_hit = None
        # TV attributes
        self.exit_id = exit_id
        self.exit_bar_index = None
        self.exit_comment = None


class TVStrategy:
    long = "BUY"
    short = "SELL"

    def __init__(self, title, shorttitle, overlay=False, pyramiding: int = 0, initial_capital=1000000,
                 default_qty_value=1):
        self.pending_orders = []
        self.opentrades = []
        self.closedtrades = []
        self.pyramiding = pyramiding
        self.initial_capital = initial_capital
        self.default_qty_value = default_qty_value
        # self.opentrades = 0
        self.position_size = 0

    def _reverse_direction(self, direction):
        return self.long if direction == self.short else self.short

    def entry_id(self, trade_num: int) -> int:
        return self.opentrades[trade_num].entry_id if len(self.opentrades) > 0 else None

    def _can_open_trade(self):
        return self.pyramiding > len(self.opentrades) if self._can_pyramids() else True

    def _can_pyramids(self):
        return self.pyramiding > 0

    def has_opentrades(self):
        return len(self.opentrades) > 0

    def get_default_qty(self, qty):
        return qty if qty else self.default_qty_value

    def get_qty(self, order, qty):
        qty = self.get_default_qty(qty)
        return qty if order.is_long() else qty * -1

    def entry(self, id, direction, qty=None, limit=None, stop=None, comment=None):

        # Case 1: No open orders
        if not self.has_opentrades():
            qty = self.get_default_qty(qty)
            order = EntryOrder(id, direction, qty)
            order.signal = comment
            self.pending_orders.append(order)
        else:
            # Case 2: Open a new order in the opposite direction
            entry_order = self.opentrades[-1]
            if entry_order.direction != direction:
                # Case 2.1 A quantity is specified, so we close according to the qty
                if qty:
                    if qty > entry_order.contracts:
                        # Close the previous order
                        self.close(entry_order.entry_id, comment=comment, qty=entry_order.contracts)
                        # Compute the new qty minus the qty used to close the previous order
                        new_entry_qty = qty - entry_order.contracts
                        # Open the new order
                        order = EntryOrder(id, direction, new_entry_qty)
                        order.signal = comment
                        self.pending_orders.append(order)
                    elif qty <= entry_order.contracts:
                        # Close the previous order
                        self.close(entry_order.entry_id, comment=comment, qty=entry_order.contracts)

                # Case 2.2: No qty is specified, so we close all previous order
                else:
                    # Close the previous order
                    self.close(entry_order.entry_id, comment=comment, qty=entry_order.contracts)
                    # Open the new order
                    order = EntryOrder(id, direction, self.default_qty_value)
                    order.signal = comment
                    self.pending_orders.append(order)

            # Case 3: Open a new order in the same direction
            elif len(self.opentrades) < self.pyramiding:
                if not qty:
                    qty = self.default_qty_value
                # Open the new order
                order = EntryOrder(id, direction, qty)
                order.signal = comment
                self.pending_orders.append(order)

    def close_all(self, comment=None, alert_message=None, immediately=False):

        if len(self.opentrades) > 0:
            entry_order = self.opentrades[-1]
            if entry_order.is_entry():
                self.close(entry_order.entry_id, comment, alert_message, immediately)

    def close(self, id, comment=None, qty=None, qty_percent=None, alert_message=None, immediately=False):
        entry_trades = [o for o in self.opentrades if o.entry_id == id]
        for entry_trade in entry_trades:
            assert entry_trade.is_entry()
            close_order = ExitOrder(id, self._reverse_direction(entry_trade.direction), qty, entry_trade.trade_num)
            close_order.signal = comment
            self.pending_orders.append(close_order)

    def exit(self, id, from_entry=None, qty=None, qty_percent=100, profit=None, limit=None, loss=None, stop=None,
             trail_price=None, trail_points=None, trail_offset=None, oca_name=None, comment=None, comment_profit=None,
             comment_loss=None, comment_trailing=None, alert_message=None, alert_profit=None, alert_loss=None,
             alert_trailing=None):
        assert 0 < qty_percent <= 100
        matching_entry_orders = [o for o in self.pending_orders + self.opentrades if o.entry_id == from_entry]
        matching_entry_order = matching_entry_orders[-1]  # FIXME Manage only the last entry orders

        if not qty:
            qty = int(abs(matching_entry_order.contracts) * qty_percent / 100)

        direction = self._reverse_direction(matching_entry_order.direction)
        order = ExitOrder(id, direction, qty, trade_num=matching_entry_order.trade_num)
        # We can't compute the loss/profit now as the entry order might not have been proceeded yet
        order.loss = loss
        order.trail_points = trail_points
        order.trail_offset = trail_offset or 0  # FIXME
        order.signal = comment
        self.pending_orders.append(order)


class Strategy:

    def __init__(self, *args, **kwargs):
        self.strategy = TVStrategy(*args, **kwargs)

    def _set_data(self, data):
        self.time = data.index.values
        self.open = data.open.values
        self.high = data.high.values
        self.low = data.low.values
        self.close = data.close.values

    def next(self):
        raise ValueError("Needs to be implemented")


def get_highest_trail(entry_price: float, high, trail_amount: float):
    trails = list(np.arange(entry_price, high, trail_amount))
    return trails[-1] if len(trails) else None


def get_trail_price(entry_order: EntryOrder, exit_order: ExitOrder, current_bar: pd.Series):
    entry_price = None

    if entry_order.is_long():
        closest_price = current_bar.open if is_low_first(current_bar) else current_bar.high
        if current_bar.open >= exit_order.trail_offset_price:
            entry_price = rounddown(closest_price)
        else:
            entry_price = exit_order.trail_offset_price

    elif entry_order.is_short():
        closest_price = current_bar.open if is_high_first(current_bar) else roundup(current_bar.low)
        if current_bar.open <= exit_order.trail_offset_price:
            entry_price = closest_price
        else:
            entry_price = exit_order.trail_offset_price
    return entry_price


def get_trail_trigger_price(entry_order, trail_points):
    trail_amount = get_price_from_ticks(trail_points)
    return entry_order.entry_price + (trail_amount if entry_order.is_long() else trail_amount * -1)


def is_trail_offset_hit(entry_order, exit_order, current_bar: pd.Series) -> bool:
    if entry_order.is_long():
        return marketdata_crossunder(current_bar, exit_order.trail_offset_price)
    elif entry_order.is_short():
        return marketdata_crossover(current_bar, exit_order.trail_offset_price)


def is_trail_hit(entry_order, exit_order, current_bar: pd.Series) -> bool:
    if entry_order.is_long():
        return exit_order.trail_price <= roundhalfup(current_bar.high)
    elif entry_order.is_short():
        return roundhalfup(current_bar.low) <= exit_order.trail_price


def get_trail_offset_price(entry_order, exit_order, marketdata: pd.DataFrame) -> float:
    partial_marketdata = marketdata.loc[:entry_order.date_time]
    trail_offset_amount = get_price_from_ticks(exit_order.trail_offset)
    if entry_order.is_long():
        # FIXME Check the rounding
        return rounddown(partial_marketdata.high.max() - trail_offset_amount)
    elif entry_order.is_short():
        return partial_marketdata.low.min() + trail_offset_amount


class StrategyTester:

    def __init__(self, data, strategy: Strategy):
        assert (isinstance(data.index, pd.DatetimeIndex))
        self.marketdata = data.sort_index(ascending=False)
        self.strategy = strategy
        global trade_num_inc
        trade_num_inc = 0

    def _process_pending_orders(self, partial_data):
        new_pending_orders = []
        current_bar = partial_data.iloc[0]
        for pending_order in self.strategy.strategy.pending_orders:
            fill_order = False

            # Entry Order
            if pending_order.is_entry():
                fill_order = self.check_pending_entry_order(current_bar, pending_order)
            elif pending_order.is_exit():
                fill_order = self.check_pending_exit_order(partial_data, pending_order)

            if fill_order:
                self.send_order(pending_order, current_bar)
            else:
                new_pending_orders.append(pending_order)

        self.strategy.strategy.pending_orders = new_pending_orders

    def check_pending_entry_order(self, current_bar: pd.Series, entry_order: EntryOrder) -> bool:
        fill_order = False

        # Case 1: Entry Stop Limit Order
        if entry_order.limit and entry_order.stop:
            # TODO
            # fill_order = True
            pass
        # Case 2: Entry Limit Order
        elif entry_order.limit and not entry_order.stop:
            if entry_order.is_long() and current_bar.open <= entry_order.limit:
                fill_order = True
            elif entry_order.is_short() and current_bar.open >= entry_order.limit:
                fill_order = True

        # Case 3: Entry Market Order
        elif not entry_order.limit and not entry_order.stop:
            fill_order = True

        return fill_order

    def check_pending_exit_order(self, marketdata: pd.DataFrame, exit_order: ExitOrder) -> bool:
        current_bar = marketdata.iloc[0]
        fill_order = False
        stoploss_hit = False
        # trail_hit = False
        # If the entry order is not yet open, we don't process the exit trade
        if not (entry_order := self.get_opentrade(exit_order.trade_num)):
            return fill_order

        # Compute Exit Stop Loss:
        if exit_order.loss and not exit_order.stop:  # Stop param has priority over loss param
            if entry_order.is_long():
                exit_order.stop = sub_ticks(entry_order.entry_price, exit_order.loss)
            elif entry_order.is_short():
                exit_order.stop = add_ticks(entry_order.entry_price, exit_order.loss)

        # Compute the trail trigger price from the trail points
        if exit_order.trail_points and not exit_order.trail_price:
            exit_order.trail_price = get_trail_trigger_price(entry_order, exit_order.trail_points)

        # Check if the trail trigger has been hit
        if exit_order.trail_price and not exit_order.trail_hit:
            exit_order.trail_hit = is_trail_hit(entry_order, exit_order, current_bar)

        # Compute the trail offset price
        if exit_order.trail_hit and not np.isnan(exit_order.trail_offset):
            exit_order.trail_offset_price = get_trail_offset_price(entry_order, exit_order, marketdata)

        # Check if the trail offset is hit
        if exit_order.trail_hit and exit_order.trail_offset_price:
            exit_order.trail_offset_hit = is_trail_offset_hit(entry_order, exit_order, current_bar)

        # Exit Stop
        stop_loss_entry_price = None
        if exit_order.stop is not None:
            if entry_price := self.is_stoploss_hit(entry_order, exit_order, current_bar):
                stop_loss_entry_price = entry_price
                stoploss_hit = True
                fill_order = True

        # Exit Trailing
        # TradingView behavior: If the exit is on the same bar as entry, the trailing take precedence over stop
        same_bar_as_entry = entry_order.date_time == current_bar.name
        trail_entry_price = None
        # Don't manage the trailing if the stoploss is already hit
        if (same_bar_as_entry or not stoploss_hit) and exit_order.trail_price:
            if exit_order.trail_hit and exit_order.trail_offset_hit:
                #trail_entry_price = exit_order.trail_offset_price
                trail_entry_price = get_trail_price(entry_order, exit_order, current_bar)
                fill_order = True
            # Just a trail without an offset
            #elif exit_order.trail_hit and not exit_order.trail_offset:
            #    trail_entry_price = get_trail_price(entry_order, exit_order, current_bar)
            #    fill_order = True


                # exit_order.trail_offset_hit = self.is_trail_offset_hit(entry_order, exit_order, marketdata)

            # if exit_order.trail_hit:
        #
        #                if trail_entry_price:
        #                    fill_order = True

        # If stop loss and trail are triggered on the same bar, we choose the closest on High/Low from Open
        if stop_loss_entry_price and trail_entry_price:
            if entry_order.is_long():
                if current_bar.high - current_bar.open > current_bar.open - current_bar.low:
                    exit_order.entry_price = stop_loss_entry_price
                else:
                    exit_order.entry_price = trail_entry_price
            elif entry_order.is_short():
                if current_bar.high - current_bar.open < current_bar.open - current_bar.low:
                    exit_order.entry_price = stop_loss_entry_price
                else:
                    exit_order.entry_price = trail_entry_price
        elif stop_loss_entry_price:
            exit_order.entry_price = stop_loss_entry_price
        elif trail_entry_price:
            exit_order.entry_price = trail_entry_price

        # Compute Exit Take Profit:
        if exit_order.profit and exit_order.limit:  # Stop param has priority over loss param
            if entry_order.is_long():
                exit_order.limit = add_ticks(entry_order.entry_price, exit_order.profit)
            elif entry_order.is_short():
                exit_order.limit = sub_ticks(entry_order.entry_price, exit_order.profit)

        # Exit Take Profit
        if exit_order.limit:
            if entry_order.is_long():
                if current_bar.open >= exit_order.limit:  # The new bar opens at lower price than the stop
                    fill_order = True
                    exit_order.entry_price = current_bar.open
                elif current_bar.high >= exit_order.limit:  # The new bar low hit the stop
                    fill_order = True
                    exit_order.entry_price = exit_order.limit

            elif entry_order.is_short():
                if current_bar.open <= exit_order.limit:
                    fill_order = True
                    exit_order.entry_price = current_bar.open
                elif current_bar.low <= exit_order.limit:
                    fill_order = True
                    exit_order.entry_price = exit_order.limit

        # Exit Market
        if not exit_order.limit and exit_order.stop is None:
            fill_order = True
            exit_order.entry_price = current_bar.open

        return fill_order

    def is_stoploss_hit(self, entry_order, exit_order, current_bar):
        entry_price = None
        if entry_order.is_long():
            if current_bar.open <= exit_order.stop:  # The new bar opens at lower price than the stop
                entry_price = current_bar.open
            elif current_bar.low <= exit_order.stop:  # The new bar low hit the stop
                entry_price = exit_order.stop
        elif entry_order.is_short():
            if current_bar.open >= exit_order.stop:
                entry_price = current_bar.open
            elif roundhalfup(current_bar.high) >= exit_order.stop:
                entry_price = exit_order.stop

        return entry_price

    def get_opentrade(self, trade_num: int) -> EntryOrder:
        return next((o for o in self.strategy.strategy.opentrades if o.trade_num == trade_num), None)

    def get_position_size(self):
        return sum([o.contracts for o in self.strategy.strategy.opentrades])

    def send_order(self, pending_order: Order, current_bar: pd.Series):
        pending_order.date_time = current_bar.name

        if pending_order.is_entry():
            pending_order.entry_price = roundhalfup(current_bar.open)
            self.strategy.strategy.opentrades.append(pending_order)

        elif pending_order.is_exit():
            new_opentrades = []

            if open_order := self.get_opentrade(pending_order.trade_num):
                # Add entry order to the closed trades
                self.strategy.strategy.closedtrades.append(open_order)
                # Add exit order to the closed trades
                self.strategy.strategy.closedtrades.append(pending_order)
            else:
                new_opentrades = self.strategy.strategy.opentrades
            self.strategy.strategy.opentrades = new_opentrades

        # Update the position size
        self.strategy.strategy.position_size = self.get_position_size()

    def _update_opentrades(self, partial_data):
        new_opentrades_orders = []
        for opentrade in self.strategy.strategy.opentrades:
            pass
        self.strategy.strategy.opentrades = new_opentrades_orders

    def _ontick(self, marketdata):
        self.strategy._set_data(marketdata)
        # self._process_opentrades(marketdata)
        self._process_pending_orders(marketdata)

        # Move to the next round
        try:
            self.strategy.next()
        except IndexError as ie:
            print("IndexError", ie)
            pass

    def run(self):
        data_len = len(self.marketdata)

        for i in range(-1, -data_len, -1):
            partial_data = self.marketdata.iloc[i:]
            self._ontick(partial_data)

        if self.strategy.strategy.has_opentrades():
            self._process_last_orders(self.marketdata)

        # Generate TradingView List of Trades
        trades_list = process_trades_list(self.strategy.strategy.closedtrades, self.marketdata,
                                          self.strategy.strategy.initial_capital)

        # Generate TradingView Performance Summary
        performance_summary = process_performance_summary(trades_list, self.strategy.strategy.opentrades,
                                                          self.marketdata, self.strategy.strategy.initial_capital)

        # Beautify
        trades_list = trades_list.rename(columns=rename_columns)[filter_columns]

        return performance_summary, trades_list

    def _process_last_orders(self, marketdata):
        # Set the Signal to 'Open' on the last open orders to match TradingView behavior
        for openorder in self.strategy.strategy.opentrades:
            self.strategy.strategy.close(openorder.entry_id, "Open", 0)
            self._process_pending_orders(marketdata)
            last_order = self.strategy.strategy.closedtrades[-1]
            if not last_order.is_entry():
                last_order.entry_price = None
                last_order.date_time = None
                self.strategy.strategy.closedtrades[-2].contracts = None
