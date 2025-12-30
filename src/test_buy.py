# src/test_buy.py

from dotenv import load_dotenv
import os
load_dotenv()

from src.live_trading import BinanceTestnetBroker
from src.executor import TradeExecutor

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
SYMBOL = "BTCUSDT"
CSV_FILE = "live_trades.csv"

def test_buy():
    print("Running TEST BUY ...")

    # Connect to Testnet broker
    broker = BinanceTestnetBroker(API_KEY, API_SECRET, SYMBOL)
    executor = TradeExecutor(broker, CSV_FILE)

    # Execute a single BUY order
    executor.execute_trade("BUY", 0.001)

    print("TEST BUY executed successfully!")
    print(f"Check {CSV_FILE} for the trade entry.")

if __name__ == "__main__":
    test_buy()
