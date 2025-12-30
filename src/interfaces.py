from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd

class IStrategy(ABC):
    """Strategy Logic Interface"""

    @abstractmethod
    def compute_indicators(self, df_15m: pd.DataFrame, df_1h: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> str:
        """Return 'BUY', 'SELL' or 'HOLD'"""
        pass

    @abstractmethod
    def position_size(self, balance: float, price: float) -> float:
        pass

    @abstractmethod
    def should_exit(self, df: pd.DataFrame) -> bool:
        pass


class IDataFeed(ABC):
    """Abstract Data Loader"""

    @abstractmethod
    def get_candles(self, timeframe: str, limit: int = 500) -> pd.DataFrame:
        pass


class IExchangeBroker(ABC):
    """Broker/Execution Layer"""

    symbol: str

    @abstractmethod
    def place_order(self, side: str, qty: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_price(self) -> float:
        pass


