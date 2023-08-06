import math
from _decimal import ROUND_UP
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
import numpy as np
import pandas as pd

from oakscript.util import get_marketdata_range, percent, roundhalfup, safe_div

rename_columns = {'entry_price': 'Price', 'date_time': 'Date/Time',
                  'type': 'Type', 'signal': 'Signal', 'contracts': 'Contracts',
                  'trade_num': 'Trade #', 'profit': 'Profit'
                  }
filter_columns = ['Trade #', 'Type', 'Signal', 'Date/Time', 'Price', 'Contracts', 'Profit', 'Profit %', 'Cum. Profit',
                  'Cum. Profit %', 'Run-up', 'Run-up %',
                  'Drawdown', 'Drawdown %'
                  ]


def get_drawdown(marketdata, trade_entry, trade_close):
    # Trade entry price
    entry_price = roundhalfup(trade_entry['rounded_price'])
    exit_price = roundhalfup(trade_close['rounded_price']) or entry_price

    # Market data range
    entry_date, exit_date = trade_entry['date_time'], trade_close['date_time']
    if pd.isnull(exit_date):
        exit_date = None
    marketdata_range = get_marketdata_range(marketdata, entry_date, exit_date, entry_price, exit_price)

    if is_long(trade_entry):
        low = roundhalfup(marketdata_range['low'].min())
        drawdown = entry_price - low
        drawdown_pct = percent(entry_price, low)
    else:
        high = roundhalfup(marketdata_range['high'].max())
        drawdown = high - entry_price
        drawdown_pct = percent(entry_price, high)
    return round(drawdown, 2), round(abs(drawdown_pct), 2)




def process_drawdown(d, marketdata):
    d['Drawdown'] = np.nan
    d['Drawdown %'] = np.nan
    for group_name, df_group in d.groupby('trade_num'):
        trade_entry = df_group.iloc[0]
        trade_close = df_group.iloc[1]
        if not pd.isnull(trade_close['date_time']):
            drawdown, drawdown_pct = get_drawdown(marketdata, trade_entry, trade_close)
            if drawdown and drawdown_pct:
                d.loc[d['trade_num'] == group_name, 'Drawdown'] = drawdown
                d.loc[d['trade_num'] == group_name, 'Drawdown %'] = drawdown_pct
            else:
                d.loc[d['trade_num'] == group_name, 'Drawdown'] = 0.0
                d.loc[d['trade_num'] == group_name, 'Drawdown %'] = 0.0

    return d['Drawdown'].astype(float), d['Drawdown %'].astype(float)


def is_short(trade):
    return 'Short' in trade['type']


def is_long(trade):
    return 'Long' in trade['type']


def get_long_runup(equity_on_entry, min_equity, numbers_of_contracts, current_high, entry_price):
    return equity_on_entry - min_equity + numbers_of_contracts * (current_high - entry_price)


def get_short_runup(equity_on_entry, min_equity, numbers_of_contracts, current_low, entry_price):
    return equity_on_entry - min_equity + numbers_of_contracts * (entry_price - current_low)


def get_max_runup(entry, close, marketdata, initial_equity, min_equity, last_cumulated_profit):
    entry_price = entry['entry_price']
    exit_price = close['entry_price']
    numbers_of_contracts = entry['contracts']

    entry_date, exit_date = entry['date_time'], close['date_time']
    if pd.isnull(exit_date):
        exit_date = None
    marketdata_range = get_marketdata_range(marketdata, entry_date, exit_date, entry_price, exit_price)

    equity_on_entry = last_cumulated_profit + initial_equity
    runup, runup_pct = None, None
    if is_long(entry):
        high = max(marketdata_range['high'].max(), exit_price)
        runup = get_long_runup(equity_on_entry, min_equity, numbers_of_contracts, high, entry_price)
        runup_pct = percent(entry_price, high)

    elif is_short(entry):
        low = min(marketdata_range['low'].min(), exit_price)
        runup = get_long_runup(initial_equity, min_equity, numbers_of_contracts, low, entry_price)
        runup_pct = percent(entry_price, low)

    return abs(runup), runup_pct


def get_runup(entry, exit, marketdata):
    if not np.isnan(exit['entry_price']):
        # Trade entry price
        entry_price = roundhalfup(entry['entry_price'])
        exit_price = roundhalfup(exit['entry_price'])

        entry_date, exit_date = entry['date_time'], exit['date_time']
        if pd.isnull(exit_date):
            exit_date = None
        marketdata_range = get_marketdata_range(marketdata, entry_date, exit_date, entry_price, exit_price)

        if is_short(entry):
            low = min(roundhalfup(marketdata_range['low'].min()), exit_price)
            runup = entry_price - low
            runup_pct = percent(entry_price, low)
        else:
            high = max(roundhalfup(marketdata_range['high'].max()), exit_price)
            open_price = marketdata_range.iloc[-1].open  # Get the price not rounded
            if entry_price == roundhalfup(open_price):
                runup = high - round(open_price, 2)
            else:
                runup = high - entry_price
            runup_pct = percent(entry_price, high)
        return max(runup, 0), runup_pct
    else:
        return None, None


def process_max_runup(d, marketdata, initial_equity):
    min_equity = initial_equity
    max_run_up = 0

    for group_name, df_group in d.groupby('trade_num'):
        trade_entry = df_group.iloc[0]
        trade_close = df_group.iloc[1]

        if not pd.isnull(trade_close['date_time']):
            last_cumulated_profit = d.iloc[trade_entry.name - 1]['Cum. Profit']
            min_equity = min(min_equity, last_cumulated_profit + initial_equity)

            runup, runup_pct = get_max_runup(trade_entry, trade_close, marketdata, initial_equity, min_equity,
                                             last_cumulated_profit)
            if runup is not None:
                max_run_up = max(max_run_up, runup)

    return max_run_up


def process_runup(d, marketdata, initial_equity):
    d['Run-up'] = np.nan
    d['Run-up %'] = np.nan
    for group_name, df_group in d.groupby('trade_num'):
        trade_entry = df_group.iloc[0]
        trade_close = df_group.iloc[1]

        if not pd.isnull(trade_close['date_time']):
            runup, runup_pct = get_runup(trade_entry, trade_close, marketdata)
            if runup is not None:
                d.loc[d['trade_num'] == group_name, 'Run-up'] = round(runup, 2)
                d.loc[d['trade_num'] == group_name, 'Run-up %'] = round(abs(runup_pct), 2)

    return d['Run-up'].astype(float), d['Run-up %'].astype(float)


def process_cumulative_profit_pct(d, initial_capital=1000000):
    d['Cum. Profit %'] = round(d[d['type'].str.startswith('Exit')]['profit'] / (
            initial_capital + d[d['type'].str.startswith('Exit')]['Cum. Profit']) * 100, 2)
    d['Cum. Profit %'] = d.groupby('trade_num', sort=False)['Cum. Profit %'].apply(
        lambda x: x.ffill().bfill())
    return d['Cum. Profit %']


def get_profit_pct(entry, close):
    if not np.isnan(entry['entry_price']):
        entry_price = roundhalfup(entry['entry_price'])
        close_price = roundhalfup(close['entry_price'])

        if is_short(entry):
            profit_pct = -percent(entry_price, close_price)
        else:
            profit_pct = percent(entry_price, close_price)
        return round(profit_pct, 2)
    else:
        return np.nan


def process_profit_pct(d):
    for group_name, df_group in d.groupby('trade_num'):
        trade_entry = df_group.iloc[0]
        trade_close = df_group.iloc[1]
        d.loc[d['trade_num'] == group_name, 'Profit %'] = get_profit_pct(trade_entry, trade_close)
    return d['Profit %']


def process_cumulative_profit(d):
    d["Cum. Profit"] = d[d['type'].str.startswith('Exit')]['profit'].cumsum()
    d['Cum. Profit'] = d.groupby('trade_num', sort=False)['Cum. Profit'].apply(
        lambda x: x.ffill().bfill())
    return d['Cum. Profit']


def process_profit(d):
    d['rounded_price'] = d['entry_price'].apply(lambda x: roundhalfup(x))
    d['shift'] = d.groupby('trade_num')['rounded_price'].shift()
    d['profit'] = np.where(d['type'].str.contains('Long'),
                           d['rounded_price'] - d['shift'],
                           d['shift'] - d['rounded_price'])

    # Copy the profit value to both rows
    d['profit'] = d.groupby('trade_num')['profit'].apply(lambda x: x.ffill().bfill())
    return d['profit']


def process_trades_list(positions, data, initial_capital):
    df_trades = pd.DataFrame([o.__dict__ for o in positions])
    # df_trades['entry_price'] = round(df_trades['entry_price'], 2)

    # df_trades['date_time'] = df_trades['date_time'].dt.date
    # df_trades[['profit', 'Cum. Profit', 'Run-up', 'Drawdown']] = None
    # TODO move code prior to rename column
    df_trades['profit'] = process_profit(df_trades)
    df_trades['Cum. Profit'] = process_cumulative_profit(df_trades)
    df_trades['Profit %'] = process_profit_pct(df_trades)
    # TODO Get the initial equity for cum profit pct
    df_trades['Cum. Profit %'] = process_cumulative_profit_pct(df_trades)
    df_trades['Run-up'], df_trades['Run-up %'] = process_runup(df_trades, data, initial_capital)
    df_trades['Drawdown'], df_trades['Drawdown %'] = process_drawdown(df_trades, data)

    df_trades['entry_price'] = df_trades['entry_price'].map(lambda x: roundhalfup(x))
    # df_trades['profit'] = df_trades['profit'].map(
    #    lambda x: roundup(x))
    df_trades['Cum. Profit'] = df_trades['Cum. Profit'].map(lambda x: roundhalfup(x))

    df_trades['contracts'] = df_trades['contracts'].map(lambda x: abs(x) if x != 0 else np.nan)
    # df_trades.iloc[-1]['contracts'] = np.nan
    return df_trades  # .rename(columns=rename_columns)[filter_columns]


def get_sharpe_ratio(return_series, N, rf):
    mean = return_series.mean() * N - rf
    sigma = return_series.std() * np.sqrt(N)
    return mean / sigma


# Max Drawdown
def get_max_drawdown(marketdata, trades_list):
    gb = trades_list.groupby('trade_num').groups
    last_trade_num = list(gb)[-1]
    last_trade_entry = trades_list.iloc[gb[last_trade_num][0]]
    entry_price = last_trade_entry['entry_price']
    entry_date = last_trade_entry['date_time']
    lowest_price = marketdata.loc[:entry_date]['low'].min()
    highest_price = marketdata.loc[:entry_date]['high'].max()

    if 'Long' in last_trade_entry['type']:
        dd = lowest_price - entry_price
    else:
        dd = entry_price - highest_price
    profits = trades_list[trades_list['type'].str.startswith('Entry')]['profit'].values
    dd = roundhalfup(dd)
    profits = np.append(profits, dd)
    profits = profits[~np.isnan(profits)]
    cs = np.cumsum(profits)
    max_dd = np.max(cs) - np.min(cs)
    return max_dd


def process_performance_summary(trades_list, market_positions, marketdata, initial_capital):
    cols = ["Title", "All", "All %", "Long", "Long %", "Short", "Short %"]
    df_perf = pd.DataFrame(columns=cols)
    performance_summary = [cols]

    net_profit = roundhalfup(trades_list['profit'].sum() / 2)
    net_profit_perc = roundhalfup(percent(initial_capital, initial_capital + net_profit))
    net_profit_long = roundhalfup(trades_list[trades_list['type'].str.contains('Long')]['profit'].sum() / 2)
    net_profit_long_perc = roundhalfup(percent(initial_capital, initial_capital + net_profit_long))
    net_profit_short = roundhalfup(trades_list[trades_list['type'].str.contains('Short')]['profit'].sum() / 2)
    net_profit_short_perc = roundhalfup(percent(initial_capital, initial_capital + net_profit_short))
    net_profit_series = pd.Series(
        ["Net Profit", net_profit, net_profit_perc, net_profit_long, net_profit_long_perc, net_profit_short,
         net_profit_short_perc],
        index=cols)
    df_perf = pd.concat([df_perf, net_profit_series.to_frame().T], ignore_index=True)

    gross_profit = roundhalfup(trades_list[trades_list['profit'] > 0]['profit'].sum() / 2)
    gross_profit_perc = roundhalfup(percent(initial_capital, initial_capital + gross_profit))
    gross_profit_long = roundhalfup(
        trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Long'))]['profit'].sum() / 2)
    gross_profit_long_perc = roundhalfup(percent(initial_capital, initial_capital + gross_profit_long))
    gross_profit_short = roundhalfup(
        trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Short'))]['profit'].sum() / 2)
    gross_profit_short_perc = roundhalfup(percent(initial_capital, initial_capital + gross_profit_short))
    gross_profit_series = pd.Series(
        ["Gross Profit", gross_profit, gross_profit_perc, gross_profit_long, gross_profit_long_perc, gross_profit_short,
         gross_profit_short_perc], index=cols)
    df_perf = pd.concat([df_perf, gross_profit_series.to_frame().T], ignore_index=True)

    gross_loss = abs(roundhalfup(trades_list[trades_list['profit'] < 0]['profit'].sum() / 2))
    gross_loss_perc = roundhalfup(percent(initial_capital, initial_capital + gross_loss))
    gross_loss_long = abs(roundhalfup(
        trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Long'))]['profit'].sum() / 2))
    gross_loss_long_perc = roundhalfup(percent(initial_capital, initial_capital + gross_loss_long))
    gross_loss_short = abs(roundhalfup(
        trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Short'))]['profit'].sum() / 2))
    gross_loss_short_perc = roundhalfup(percent(initial_capital, initial_capital + gross_loss_short))
    gross_loss_series = pd.Series(
        ["Gross Loss", gross_loss, gross_loss_perc, gross_loss_long, gross_loss_long_perc, gross_loss_short,
         gross_loss_short_perc],
        index=cols)
    df_perf = pd.concat([df_perf, gross_loss_series.to_frame().T], ignore_index=True)

    max_runup = process_max_runup(trades_list, marketdata, initial_capital)  # trades_list['Run-up'].max()
    max_runup_perc = roundhalfup(percent(initial_capital, initial_capital + max_runup))
    df_perf = pd.concat([df_perf, pd.Series(["Max Run-up", max_runup, max_runup_perc], index=cols[:3]).to_frame().T])

    max_drawdown = get_max_drawdown(marketdata, trades_list)
    max_drawdown_perc = roundhalfup(percent(initial_capital, initial_capital + max_drawdown))
    df_perf = pd.concat(
        [df_perf, pd.Series(["Max Drawdown", max_drawdown, max_drawdown_perc], index=cols[:3]).to_frame().T],
        ignore_index=True)

    # Buy & Hold
    first_trade_price = trades_list.iloc[0]['entry_price']
    last_price = marketdata.iloc[0].close
    buy_shares = int(initial_capital / first_trade_price)
    buy_and_hold = buy_shares * last_price - initial_capital
    buy_and_hold_perc = roundhalfup(buy_and_hold / initial_capital * 100)
    df_perf = pd.concat([df_perf, pd.Series(
        ["Buy & Hold Return", buy_and_hold, buy_and_hold_perc], index=cols[:3]).to_frame().T], ignore_index=True)

    # Sharpe Ratio
    """The formula for the Sharpe ratio is SR = (MR - RFR) / SD, where MR is the average return for a period (monthly 
    for a trading period of 3 or more months or daily for a trading period of 3 or more days), and RFR is the 
    risk-free rate of return (by default, 2% annually. Can be changed with the "risk_free_rate" parameter of the 
    "strategy()" function). SD is the standard deviation of returns."""

    risk_free_rate = 2
    monthly_adj = (21 ** 0.5)

    N = 21  # 21 trading days per month
    rf = 0.02  # 2% risk-free rate
    sharpe_ratio = roundhalfup(get_sharpe_ratio(trades_list['profit'], N, rf, ) * 100)

    df_perf = pd.concat([df_perf, pd.Series(
        ["Sharpe Ratio", sharpe_ratio], index=cols[:2]).to_frame().T], ignore_index=True)

    # Sortino Ratio
    """The formula for the Sortino ratio is SR = (MR - RFR) / DD, where MR is the average return for a period (
    monthly for a trading period of 3 or more months or daily for a trading period of 3 or more days), and RFR is the 
    risk-free rate of return (by default, 2% annually. Can be changed with the "risk_free_rate" parameter of the 
    "strategy()" function). DD is the downside deviation of returns = sqrt(sum(min(0, Xi - T))^2/N), where Xi - ith 
    return, N - total number of returns, T - target return."""

    def get_sortino_ratio(series, N, rf):
        mean = series.mean() * N - rf
        std_neg = series[series < 0].std() * np.sqrt(N)
        return mean / std_neg

    sortinos = roundhalfup(get_sortino_ratio(trades_list['profit'], N, rf, ) * 100)

    df_perf = pd.concat([df_perf, pd.Series(
        ["Sortino Ratio", sortinos], index=cols[:2]).to_frame().T], ignore_index=True)

    # Calmar Ratios
    # calmars = roundup(trades_list['profit'].mean() * 255 / abs(trades_list['Drawdown'].max()))

    # df_perf = pd.concat([df_perf, pd.Series(
    #    ["Calmar Ratio", calmars], index=cols[:2]).to_frame().T], ignore_index=True)

    # Profit Factor
    profit_factor = round(safe_div(gross_profit, gross_loss), 3)
    profit_factor_long = round(safe_div(gross_profit_long, gross_loss_long), 3)
    profit_factor_short = round(safe_div(gross_profit_short, gross_loss_short), 3)
    df_perf = pd.concat([df_perf, pd.Series(
        ["Profit Factor", profit_factor, np.nan, profit_factor_long, np.nan, profit_factor_short, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Max Contracts Held
    max_contract_helds = 1
    df_perf = pd.concat([df_perf, pd.Series(
        ["Max Contracts Held", max_contract_helds, np.nan, max_contract_helds, np.nan, max_contract_helds, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Open PL
    # TODO
    df_perf = pd.concat([df_perf, pd.Series(
        ["Open PL", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        index=cols).to_frame().T], ignore_index=True)
    # Commission Paid
    # TODO
    df_perf = pd.concat([df_perf, pd.Series(
        ["Commission Paid", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Total Closed Trades
    closed_trades = trades_list[(trades_list['type'].str.startswith('Exit')) & (~trades_list['entry_price'].isnull())]
    total_closed_trades = closed_trades['type'].count()

    closed_trades_long = closed_trades.loc[trades_list['type'].str.contains('Long')]
    total_closed_trades_long = closed_trades_long['type'].count()

    total_closed_trades_short = \
        trades_list[(trades_list['type'].str.startswith('Exit')) & (trades_list['type'].str.contains('Short'))][
            'contracts'].count()
    df_perf = pd.concat([df_perf, pd.Series(
        ["Total Closed Trades", total_closed_trades, np.nan, total_closed_trades_long, np.nan,
         total_closed_trades_short, np.nan], index=cols).to_frame().T], ignore_index=True)

    # Total Open Trades
    total_opened_trades = trades_list[trades_list['type'].str.startswith('Entry')]['type'].count()
    total_opened_trades_long = \
        trades_list[(trades_list['type'].str.startswith('Entry')) & (trades_list['type'].str.contains('Long'))][
            'type'].count()
    total_opened_trades_short = \
        trades_list[(trades_list['type'].str.startswith('Entry')) & (trades_list['type'].str.contains('Short'))][
            'type'].count()
    df_perf = pd.concat([df_perf, pd.Series(
        ["Total Open Trades", total_opened_trades - total_closed_trades, np.nan,
         total_opened_trades_long - total_closed_trades_long, np.nan,
         total_opened_trades_short - total_closed_trades_short, np.nan], index=cols).to_frame().T],
                        ignore_index=True)

    # Number Winning Trades
    winning_trades = trades_list[trades_list['profit'] > 0]['profit'].count() / 2
    winning_trades_long = trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Long'))][
                              'profit'].count() / 2
    winning_trades_short = trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Short'))][
                               'profit'].count() / 2
    df_perf = pd.concat([df_perf, pd.Series(
        ["Number Winning Trades", winning_trades, np.nan, winning_trades_long, np.nan, winning_trades_short, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Number Losing Trades
    losing_trades = trades_list[trades_list['profit'] < 0]['profit'].count() / 2
    losing_trades_long = trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Long'))][
                             'profit'].count() / 2
    losing_trades_short = trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Short'))][
                              'profit'].count() / 2
    df_perf = pd.concat([df_perf, pd.Series(
        ["Number Losing Trades", losing_trades, np.nan, losing_trades_long, np.nan, losing_trades_short, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Percent Profitable
    percent_profitable = round(100 - (100 * (total_closed_trades - winning_trades) / total_closed_trades), 2)
    percent_profitable_long = round(
        100 - (100 * (total_closed_trades_long - winning_trades_long) / total_closed_trades_long), 2)
    percent_profitable_short = round(
        100 - (100 * (total_closed_trades_short - winning_trades_short) / total_closed_trades_short), 2)
    df_perf = pd.concat([df_perf, pd.Series(
        ["Percent Profitable", percent_profitable, np.nan, percent_profitable_long, np.nan, percent_profitable_short,
         np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Avg Trade
    avg_trade = roundhalfup(trades_list['profit'].mean())
    avg_trade_long = roundhalfup(trades_list[(trades_list['type'].str.contains('Long'))]['profit'].mean())
    avg_trade_short = roundhalfup(trades_list[(trades_list['type'].str.contains('Short'))]['profit'].mean())
    df_perf = pd.concat([df_perf, pd.Series(
        ["Avg Trade", avg_trade, None, avg_trade_long, np.nan, avg_trade_short, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Avg Winning Trade
    avg_winning_trade = roundhalfup(trades_list[(trades_list['profit'] > 0)]['profit'].mean())
    avg_winning_trade_long = roundhalfup(
        trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Long'))]['profit'].mean())
    avg_winning_trade_short = roundhalfup(
        trades_list[(trades_list['profit'] > 0) & (trades_list['type'].str.contains('Short'))]['profit'].mean())
    df_perf = pd.concat([df_perf, pd.Series(
        ["Avg Winning Trade", avg_winning_trade, np.nan, avg_winning_trade_long, np.nan, avg_winning_trade_short,
         np.nan],
        index=cols).to_frame().T], ignore_index=True)

    # Avg Losing Trade
    avg_losing_trade = abs(roundhalfup(trades_list[(trades_list['profit'] < 0)]['profit'].mean()))
    avg_losing_trade_long = abs(
        roundhalfup(
            trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Long'))]['profit'].mean()))
    avg_losing_trade_short = abs(roundhalfup(
        trades_list[(trades_list['profit'] < 0) & (trades_list['type'].str.contains('Short'))]['profit'].mean()))
    df_perf = pd.concat([df_perf, pd.Series(
        ["Avg Losing Trade", avg_losing_trade, np.nan, avg_losing_trade_long, np.nan, avg_losing_trade_short, np.nan],
        index=cols).to_frame().T], ignore_index=True)

    return df_perf
