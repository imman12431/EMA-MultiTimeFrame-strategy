# src/live_trading.py

from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

import time
from binance.client import Client
from src.strategy import MultiTimeframeEMAStrategy
from src.executor import TradeExecutor
from src.data_loader import BinanceDataFeed
from src.interfaces import IExchangeBroker

class BinanceTestnetBroker(IExchangeBroker):
    """
    Broker adapter for Binance Testnet REST API
    """
    def __init__(self, api_key: str, api_secret: str, symbol: str):
        self.symbol = symbol
        self.client = Client(api_key, api_secret, testnet=True)

    def get_price(self) -> float:
        ticker = self.client.get_symbol_ticker(symbol=self.symbol)
        return float(ticker["price"])


    def place_order(self, side: str, qty: float):
        order = self.client.create_test_order(
            symbol=self.symbol,
            side=side,
            type="MARKET",
            quantity=qty
        )
        return order

def run_live_trading(symbol="BTCUSDT", csv_file="live_trades.csv", sleep_sec=60):
    api_key = API_KEY
    api_secret = API_SECRET
    datafeed = BinanceDataFeed(symbol)
    strategy = MultiTimeframeEMAStrategy(position_qty=0.001)
    broker = BinanceTestnetBroker(api_key, api_secret, symbol)
    executor = TradeExecutor(broker, csv_file)

    print("Starting live trading loop. Press Ctrl+C to stop.")

    try:
        while True:
            df_15m = datafeed.get_candles("15m")
            df_1h = datafeed.get_candles("1h")
            df_combined = strategy.compute_indicators(df_15m, df_1h)

            last = df_combined.iloc[-1]
            print(
                f"time {last.name} | Price {last['close']:.2f} | "
                f"EMA10 {last['EMA10']:.2f} | EMA20 {last['EMA20']:.2f} | "
                f"Trend: 50h {last['EMA50_1h']:.2f} > 200h {last['EMA200_1h']:.2f}"
            )

            # evaluate strategy
            exit_signal = strategy.should_exit(df_combined)
            entry_signal = strategy.generate_signal(df_combined)

            print(f" entry={entry_signal}   exit={exit_signal}")

            if exit_signal:
                executor.execute_trade("SELL", strategy.position_qty)
            if entry_signal == "BUY":
                executor.execute_trade("BUY", strategy.position_qty)

            time.sleep(sleep_sec)

    except KeyboardInterrupt:
        print("Live trading stopped by user.")

if __name__ == "__main__":
    run_live_trading()