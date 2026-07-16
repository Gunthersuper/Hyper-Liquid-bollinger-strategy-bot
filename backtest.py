import pandas as pd
from time import sleep
import ta
from backtesting import Backtest, Strategy
from hyperliquid.utils import constants
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from utils import setup, klines, get_pnl, market_order, market_close, get_position_side, total_positions, get_balance, coin_limit_price
address, info, exchange = setup(base_url=constants.MAINNET_API_URL, skip_ws=True)

def bol_h(df, period=40, dev=2):
    return ta.volatility.BollingerBands(pd.Series(df), window=period, window_dev=dev).bollinger_hband()


def bol_l(df, period=40, dev=2):
    return ta.volatility.BollingerBands(pd.Series(df), window=period, window_dev=dev).bollinger_lband()


class str(Strategy):
    bol_period = 23
    bol_dev = 1

    def init(self):
        self.bol_h = self.I(bol_h, self.data.Close, self.bol_period, self.bol_dev)
        self.bol_l = self.I(bol_l, self.data.Close, self.bol_period, self.bol_dev)

    def next(self):
        if self.data.Close[-2] > self.bol_l[-2] and self.data.Close[-1] < self.bol_l[-1]:
            if not self.position:
                self.buy(size=0.5)
            if self.position.is_short:
                self.position.close()
                self.buy(size=0.5)

        if self.data.Close[-2] < self.bol_h[-2] and self.data.Close[-1] > self.bol_h[-1]:
            if not self.position:
                self.sell(size=0.5)
            if self.position.is_long:
                self.position.close()
                self.sell(size=0.5)


# symbols = get_tickers_usdt()
symbol = 'HYPE'
timeframe = '1m'
interval = 2000  # candles
kl = klines(info, symbol, timeframe, interval)
bt = Backtest(kl, str, cash=500, margin=1/10, commission=0.0007)

# print(get_balance(info, address))



# stats = bt.run()

stats, heatmap = bt.optimize(
    bol_period=range(5, 60, 1),
    bol_dev=range(1, 2, 1),
    maximize='Equity Final [$]',
    max_tries=20000,
    random_state=0,
    return_heatmap=True)

print(stats)
bt.plot()
# print(heatmap)
# result = pd.DataFrame(heatmap)
# result.to_excel('heatmap.xlsx')