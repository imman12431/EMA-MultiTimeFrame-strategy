# src/backtest.py

import pandas as pd
from backtesting import Backtest, Strategy
from src.strategy import MultiTimeframeEMAStrategy
from src.data_loader import BinanceDataFeed
from src.executor import TradeExecutor
from src.interfaces import IExchangeBroker

class BacktestBroker(IExchangeBroker):
    """
    Minimal broker adapter for backtesting
    """
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_price(self):
        # In backtest, use close price of last candle
        return self.last_close

    def place_order(self, side: str, qty: float):
        # In backtest, order always fills at close price
        return {"status": "FILLED", "side": side, "qty": qty, "price": self.last_close}



def run_backtest(symbol="BTCUSDT", csv_file="backtest_trades.csv"):
    # Load historical candles
    datafeed = BinanceDataFeed(symbol)
    df_15m = datafeed.get_candles("15m")
    df_1h = datafeed.get_candles("1h")

    strategy_obj = MultiTimeframeEMAStrategy(position_qty=0.001)
    df_combined = strategy_obj.compute_indicators(df_15m, df_1h)

    broker = BacktestBroker(symbol)
    executor = TradeExecutor(broker, csv_file)

    # Loop through each 15m candle
    for i in range(len(df_combined)):
        broker.last_close = df_combined["close"].iloc[i]

        if strategy_obj.should_exit(df_combined.iloc[:i+1]):
            executor.execute_trade("SELL", strategy_obj.position_qty)

        signal = strategy_obj.generate_signal(df_combined.iloc[:i+1])
        if signal == "BUY":
            executor.execute_trade("BUY", strategy_obj.position_qty)

    print(f"Backtest completed. Trades saved to {csv_file}")

if __name__ == "__main__":
    run_backtest()