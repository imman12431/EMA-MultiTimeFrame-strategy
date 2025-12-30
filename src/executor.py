# src/executor.py

import csv
from datetime import datetime
from src.interfaces import IExchangeBroker

class TradeExecutor:
    """
    Executes trades using a broker (real or backtest)
    Logs trades to CSV
    """

    def __init__(self, broker: IExchangeBroker, csv_file: str):
        self.broker = broker
        self.csv_file = csv_file

        # Initialize CSV with headers if file does not exist
        try:
            with open(self.csv_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "symbol", "side", "qty", "price"])
        except FileExistsError:
            pass

    def execute_trade(self, side: str, qty: float):
        """
        Place order using broker and log to CSV
        """
        price = self.broker.get_price()
        order = self.broker.place_order(side, qty)
        timestamp = datetime.utcnow().isoformat()

        # Log to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, self.broker.symbol, side, qty, price])

        return order
