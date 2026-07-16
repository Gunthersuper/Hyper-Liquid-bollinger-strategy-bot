from hyperliquid.utils import constants
import json
import time
import pandas as pd
from utils import setup, klines, get_pnl, market_order, market_close, get_position_side, total_positions, get_balance, coin_limit_price, get_state
import ta

address, info, exchange = setup(base_url=constants.MAINNET_API_URL, skip_ws=True)
print(exchange.set_referrer("GUNTHER"))

coin = 'PUMP'
timeframe = '1m'
leverage = 10

win = 21
dev = 1

def bol(coin, timeframe, win, dev):
    kl = klines(info, coin, timeframe=timeframe, interval=2000)
    low = ta.volatility.BollingerBands(kl.Close, window=win, window_dev=dev).bollinger_lband()
    high = ta.volatility.BollingerBands(kl.Close, window=win, window_dev=dev).bollinger_hband()
    if float(kl.Close.iloc[-2]) > float(low.iloc[-2]) and float(kl.Close.iloc[-1]) < float(low.iloc[-1]):
        return True
    if float(kl.Close.iloc[-2]) < float(high.iloc[-2]) and float(kl.Close.iloc[-1]) > float(high.iloc[-1]):
        return False


while True:
    try:
        position_side = get_position_side(info, address, coin)
        balance = get_balance(info, address)
        pnl = get_pnl(info, address, coin)
        print('Balance:',balance)
        print('Position: ', position_side)
        print('Pnl: ', pnl, 'USDC')
        time.sleep(1)
        price = coin_limit_price(info, coin)
        print('Price:',price)
        margin = round(((balance/2)/price)*leverage)
        time.sleep(1)
        signal = bol(coin, timeframe, win , dev)
        if signal is not None:
            if position_side is None:
                print('Found a signal - ', signal)
                market_order(exchange, coin, signal, margin)
            if position_side == 'long' and signal is False:
                print('Have long position, Found SELL signal')
                market_close(exchange, coin)
                time.sleep(1)
                market_order(exchange, coin, signal, margin)
            if position_side == 'short' and signal is True:
                print('Have short position, Found BUY signal')
                market_close(exchange, coin)
                time.sleep(1)
                market_order(exchange, coin, signal, margin)
        print('Signal: ', signal)
        print('Wait 20 sec')
        time.sleep(20)

    except Exception as err:
        print(err)
        print('Wait 30 sec')

        time.sleep(30)
