# src/data_loader.py

import pandas as pd
import requests
from src.interfaces import IDataFeed

class BinanceDataFeed(IDataFeed):
    """
    Fetches OHLCV data from Binance (Testnet or Live)
    Provides multi-timeframe candles for the strategy
    """

    def __init__(self, symbol: str, base_url: str = "https://testnet.binance.vision/api/v3/klines"):
        self.symbol = symbol
        self.base_url = base_url

    def get_candles(self, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """
        Fetch historical candles from Binance REST API
        """
        params = {
            "symbol": self.symbol,
            "interval": timeframe,
            "limit": limit
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])

        # Convert numeric columns
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        # Convert timestamp to datetime
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)

        return df
