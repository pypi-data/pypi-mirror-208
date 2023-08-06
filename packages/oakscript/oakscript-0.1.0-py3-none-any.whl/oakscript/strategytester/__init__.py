import pandas as pd

from oakscript.strategytester.reports import process_trades_list, process_performance_summary, rename_columns, \
    filter_columns

trade_num_inc = 0


def get_trade_num():
    global trade_num_inc
    trade_num_inc += 1
    return trade_num_inc


class Order:
    def __init__(self, id: str, direction: str, qty: int, trade_num=None):
        assert id
        assert direction in ["BUY", "SELL"]
        # assert qty < 0 or qty > 0

        self.trade_num = trade_num or get_trade_num()
        self.id = id
        self.direction = direction
        self.contracts = self._get_short_qty(qty) if self.is_short() else qty
        self.limit = None
        self.stop = None
        self.comment = None
        self.entry_price = None
        self.child_orders = []
        self.type = None
        self.trail_points = None

    def _get_short_qty(self, qty):
        return qty * -1

    def is_entry(self):
        return self.type.startswith("Entry")

    def is_stop(self):
        return self.stop is not None

    def is_market(self):
        return not self.is_limit() and not self.is_stop()

    def is_exit(self):
        return self.type.startswith("Exit")

    def is_limit(self):
        return self.limit is not None

    def is_trail_points(self):
        return self.trail_points is not None

    def is_long(self):
        return self.direction == "BUY"

    def is_short(self):
        return self.direction == 'SELL'

    def _type(self, direction):
        return 'Long' if direction == "BUY" else 'Short'


class EntryOrder(Order):
    def __init__(self, id, direction, qty, trade_num=None):
        super().__init__(id, direction, qty, trade_num)
        self.type = 'Entry Long' if self.direction == "BUY" else 'Entry Short'


class ExitOrder(Order):
    def __init__(self, id, direction, qty, trade_num=None):
        super().__init__(id, direction, qty, trade_num)
        self.type = 'Exit Short' if self.direction == "BUY" else 'Exit Long'
        self.loss = None


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
        return self.opentrades[trade_num].id if len(self.opentrades) > 0 else None

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
            last_order = self.opentrades[-1]
            if last_order.direction != direction:

                # Case 2.1 A quantity is specified, so we close according to the qty
                if qty:
                    if qty > last_order.contracts:
                        # Close the previous order
                        self.close(last_order.id, comment=comment, qty=last_order.contracts)
                        # Compute the new qty minus the qty used to close the previous order
                        new_entry_qty = qty - last_order.contracts
                        # Open the new order
                        order = EntryOrder(id, direction, new_entry_qty)
                        order.signal = comment
                        self.pending_orders.append(order)
                    elif qty <= last_order.contracts:
                        # Close the previous order
                        self.close(last_order.id, comment=comment, qty=last_order.contracts)

                # Case 2.2: No qty is specified, so we close all previous order
                else:
                    # Close the previous order
                    self.close(last_order.id, comment=comment, qty=last_order.contracts)
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
            last_order = self.opentrades[-1]
            if last_order.is_entry():
                self.close(last_order.id, comment, alert_message, immediately)

    def close(self, id, comment=None, qty=None, qty_percent=None, alert_message=None, immediately=False):
        opentrades = [o for o in self.opentrades if o.id == id]
        for opentrade in opentrades:
            assert opentrade.is_entry()
            close_order = ExitOrder(id, self._reverse_direction(opentrade.direction), qty, opentrade.trade_num)
            close_order.signal = comment
            self.pending_orders.append(close_order)

    def exit(self, id, from_entry=None, qty=None, qty_percent=100, profit=None, limit=None, loss=None, stop=None,
             trail_price=None, trail_points=None, trail_offset=None, oca_name=None, comment=None, comment_profit=None,
             comment_loss=None, comment_trailing=None, alert_message=None, alert_profit=None, alert_loss=None,
             alert_trailing=None):
        assert qty_percent > 0 and qty_percent <= 100
        matching_entry_orders = [o for o in self.pending_orders + self.opentrades if o.id == from_entry]
        matching_entry_order = matching_entry_orders[-1]  # FIXME Manage only the last entry orders

        if not qty:
            qty = int(abs(matching_entry_order.contracts) * qty_percent / 100)

        direction = self._reverse_direction(matching_entry_order.direction)
        order = ExitOrder(id, direction, qty, trade_num=matching_entry_order.trade_num)
        order.loss = loss
        order.trail_points = trail_points
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


class StrategyTester:

    def __init__(self, data, strategy: Strategy):
        assert (isinstance(data.index, pd.DatetimeIndex))
        self.marketdata = data.sort_index(ascending=False)
        self.strategy = strategy
        global trade_num_inc
        trade_num_inc = 0

    def _process_pending_orders(self, partial_data):
        new_pending_orders = []
        for pending_order in self.strategy.strategy.pending_orders:
            current_bar = partial_data.iloc[0]
            current_price = current_bar.open
            fill_order = False

            # Entry Order
            if pending_order.is_entry():
                # Case 1: Entry Stop Limit Order
                if pending_order.is_limit() and pending_order.is_stop():
                    # TODO
                    # fill_order = True
                    pass
                # Case 2: Entry Limit Order
                elif pending_order.is_limit() and not pending_order.is_stop():
                    if pending_order.is_long() and current_price <= pending_order.limit:
                        fill_order = True
                    elif pending_order.is_short() and current_price >= pending_order.limit:
                        fill_order = True

                # Case 3: Entry Market Order
                elif pending_order.is_market():
                    fill_order = True
                else:
                    raise ValueError("Unknown Entry order", pending_order.id)
            elif pending_order.is_exit():
                # TODO Check if entry is in the open orders
                # Case: Update Trailing
                if pending_order.is_trail_points():
                    for entry_order in self.strategy.strategy.opentrades:
                        if entry_order.trade_num == pending_order.trade_num:
                            self.process_trail_orders(entry_order, pending_order, current_bar)

                # Case: Exit Stop Limit Order
                if pending_order.is_limit():
                    if pending_order.is_stop():
                        print("#TODO Stop-limit Order not yet implemented")
                        # TODO
                        # fill_order = True
                    # Case: Exit Limit/Loss Order
                    else:
                        for open_order in self.strategy.strategy.opentrades:
                            if open_order.trade_num == pending_order.trade_num:
                                if open_order.is_long() and self.is_below_limit(current_bar, pending_order.limit):
                                    fill_order = True
                                elif open_order.is_short() and self.is_above_limit(current_bar, pending_order.limit):
                                    fill_order = True
                # Case: Exit Market Order
                elif pending_order.is_market():
                    fill_order = True
                else:
                    raise ValueError("Unknown Exit order", pending_order.id)
            else:
                raise ValueError("Unknown order", pending_order.id)

            if fill_order:
                pending_order.date_time = partial_data.index[0]
                pending_order.entry_price = partial_data.iloc[0].open

                if pending_order.is_entry():
                    self.strategy.strategy.opentrades.append(pending_order)
                    self.strategy.strategy.position_size += pending_order.contracts
                    self.update_exit_orders(pending_order, current_bar)

                elif pending_order.is_exit():
                    new_opentrades = []
                    if pending_order.is_limit():
                        if pending_order.is_long():
                            pending_order.entry_price = current_bar.open \
                                if current_bar.open < pending_order.limit else pending_order.limit
                        elif pending_order.is_short():
                            pending_order.entry_price = current_bar.open \
                                if current_bar.open > pending_order.limit else pending_order.limit

                    for open_order in self.strategy.strategy.opentrades:
                        if open_order.trade_num == pending_order.trade_num:
                            self.strategy.strategy.closedtrades.append(open_order)
                            self.strategy.strategy.closedtrades.append(pending_order)
                            self.strategy.strategy.position_size += pending_order.contracts
                        else:
                            new_opentrades.append(open_order)
                    self.strategy.strategy.opentrades = new_opentrades
            else:
                new_pending_orders.append(pending_order)

        self.strategy.strategy.pending_orders = new_pending_orders

    def update_exit_orders(self, entry_order, current_bar):
        for pending_order in self.strategy.strategy.pending_orders:
            if pending_order.is_exit() and pending_order.trade_num == entry_order.trade_num:

                if pending_order.loss:
                    pending_order.limit = self.get_limit_from_loss(entry_order, pending_order.loss)

    def update_exit_order(self, entry_order, exit_order, current_bar: pd.Series):
        # Loss turn to limit
        if exit_order.loss:
            exit_order.limit = self.get_limit_from_loss(entry_order, exit_order.loss)

    def process_trail_orders(self, entry_order, exit_order, current_bar: pd.Series):
        if exit_order.trail_points:
            trail_amount = exit_order.trail_points / 100
            if entry_order.is_long() and max(current_bar.close, current_bar.high) >= entry_order.entry_price + trail_amount:
                exit_order.limit = max(entry_order.entry_price + trail_amount, exit_order.limit)
            elif entry_order.is_short() and min(current_bar.close, current_bar.low) <= entry_order.entry_price - trail_amount:
                exit_order.limit = min(entry_order.entry_price - trail_amount, exit_order.limit)

    def get_limit_from_loss(self, entry_order, loss):
        limit = 0
        if entry_order.is_long():
            limit = entry_order.entry_price - (loss / 100)
        elif entry_order.is_short():
            limit = entry_order.entry_price + (loss / 100)

        if limit <= 0:
            print("Loss gives negative numbers")
        return max(limit, 0)

    def _process_opentrades(self, partial_data):
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
            self.strategy.strategy.close(openorder.id, "Open", 0)
            self._process_pending_orders(marketdata)
            last_order = self.strategy.strategy.closedtrades[-1]
            if not last_order.is_entry():
                last_order.entry_price = None
                last_order.date_time = None
                self.strategy.strategy.closedtrades[-2].contracts = None

    def is_below_limit(self, current_bar, limit):
        return current_bar.low <= limit

    def is_above_limit(self, current_bar, limit):
        return current_bar.high >= limit
