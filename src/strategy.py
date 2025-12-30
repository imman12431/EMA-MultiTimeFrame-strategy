# src/strategy.py

import pandas as pd
from src.interfaces import IStrategy

class MultiTimeframeEMAStrategy(IStrategy):
    """
    Multi-Timeframe EMA Strategy
    - 15m EMA10/EMA20: entry
    - 1h EMA50/EMA200: trend filter
    """

    def __init__(self, position_qty: float = 0.001):
        self.position_qty = position_qty
        self.active_position = None  # "LONG" or None

    def compute_indicators(self, df_15m, df_1h):
        # 15m EMAs
        df_15m["EMA10"] = df_15m["close"].ewm(span=10, adjust=False).mean()
        df_15m["EMA20"] = df_15m["close"].ewm(span=20, adjust=False).mean()

        # 1h EMAs
        df_1h["EMA50_1h"] = df_1h["close"].ewm(span=50, adjust=False).mean()
        df_1h["EMA200_1h"] = df_1h["close"].ewm(span=200, adjust=False).mean()

        # Reindex 1h candles onto 15m timestamps (forward fill)
        df_1h_resampled = df_1h[["EMA50_1h", "EMA200_1h"]].reindex(df_15m.index, method="ffill")

        # Combine into one DataFrame
        df = pd.concat([df_15m, df_1h_resampled], axis=1)

        return df

    def generate_signal(self, df: pd.DataFrame):
        """
        Entry rule: 15m EMA10 crosses above EMA20 with 1h trend filter
        Safe: returns None if not enough candles
        """
        if len(df) < 2:
            return None  # Not enough data to detect crossover

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # ENSURE TREND (1-HOUR)
        if last["EMA50_1h"] <= last["EMA200_1h"]:
            return None

        # ENTRY condition: EMA10 crosses above EMA20
        if prev["EMA10"] <= prev["EMA20"] and last["EMA10"] > last["EMA20"]:
            return "BUY"

        return None

    def position_size(self, balance: float, price: float) -> float:
        """
        Fixed position size
        """
        return self.position_qty

    def should_exit(self, df: pd.DataFrame) -> bool:
        """
        Exit rule: close position if 15m EMA10 crosses below EMA20
        Safe: returns False if not enough candles
        """
        if len(df) < 2:
            return False  # Not enough data to check crossover

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # Exit when EMA10 crosses below EMA20
        return prev["EMA10"] >= prev["EMA20"] and last["EMA10"] < last["EMA20"]
