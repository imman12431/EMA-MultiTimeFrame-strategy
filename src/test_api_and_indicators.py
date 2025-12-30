# src/test_api_and_indicators.py

from dotenv import load_dotenv
import os
load_dotenv()

import pandas as pd
from binance.client import Client
from src.data_loader import BinanceDataFeed
from src.strategy import MultiTimeframeEMAStrategy

# Load keys
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def test_api_connection():
    """
    Test Binance Testnet authentication
    """
    print("🔌 Testing Binance Testnet authentication ...")
    try:
        client = Client(API_KEY, API_SECRET, testnet=True)
        server_time = client.get_server_time()
        print(" Connected successfully. Server time:", server_time)
    except Exception as e:
        print("API error:", e)


def test_data_and_indicators(symbol="BTCUSDT"):
    """
    Fetch data + compute EMA indicators and print latest rows
    """
    print("\n Fetching candles and computing indicators...")
    datafeed = BinanceDataFeed(symbol)

    df_15m = datafeed.get_candles("15m")
    df_1h = datafeed.get_candles("1h")

    strat = MultiTimeframeEMAStrategy(position_qty=0.001)
    df = strat.compute_indicators(df_15m, df_1h)

    print("\n Last 5 rows of indicator DataFrame:")
    print(df.tail())

    print("\n Latest candle indicators:")
    last = df.iloc[-1]
    print(
        f"""
        Time: {last.name}
        Price: {last['close']}
        EMA10: {last['EMA10']}
        EMA20: {last['EMA20']}
        EMA50 (1h): {last['EMA50_1h']}
        EMA200 (1h): {last['EMA200_1h']}
        """
    )

if __name__ == "__main__":
    test_api_connection()
    test_data_and_indicators()
