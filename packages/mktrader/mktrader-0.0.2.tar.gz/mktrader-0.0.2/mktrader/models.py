from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from .logger import set_logs

"""Items in this file are database objects.
These then all relate to a table in the database.
No ORM is utilized, just straight SQL Queries with psycopg2
"""


@dataclass
class Asset():
    symbol: str
    name: str
    easy_to_borrow: bool
    exchange: str
    fractionable: bool
    id: str
    marginable: bool
    shortable: bool
    status: str
    tradable: bool
    asset_class: str
    maintenance_margin_requirement: Optional[float] = 0.00
    min_order_size: Optional[float] = 0.00
    min_trade_increment: Optional[float] = 0.00
    price_increment: Optional[float] = 0.00
    attributes: List[str] = field(default_factory=list)


@dataclass
class Candle:
    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Order:
    client_order_id: str
    symbol: str
    qty: int
    type: str
    side: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    asset_id: Optional[str] = None
    asset_class: Optional[str] = None
    status: Optional[str] = None
    filled_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    replaced_at: Optional[datetime] = None
    replaced_by: Optional[datetime] = None
    replaces: Optional[str] = None
    notional: Optional[str] = None
    filled_qty: Optional[int] = None
    filled_avg_price: Optional[float] = None
    order_class: Optional[str] = None
    order_type: Optional[str] = None
    time_in_force: Optional[str] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    extended_hours: Optional[bool] = False
    legs: Optional[List['Order']] = None
    trail_percent: Optional[str] = None
    trail_price: Optional[float] = None
    hwm: Optional[str] = None
    subtag: Optional[str] = None
    source: Optional[str] = None


@dataclass
class BracketOrder(List[Order]):
    entry_order: Order
    take_profit_order: Order
    stop_loss_order: Order

    def asAlpacaOrder(self) -> dict:
        return {
            "client_order_id": self.entry_order.client_order_id,
            "side": self.entry_order.side,
            "symbol": self.entry_order.symbol,
            "type": self.entry_order.type,
            "qty": self.entry_order.qty,
            "time_in_force": self.entry_order.time_in_force,
            "stop_price": self.entry_order.stop_price,
            "limit_price": self.entry_order.limit_price,
            "order_class": self.entry_order.order_class,
            "take_profit": {
                "limit_price": self.take_profit_order.limit_price,
                "client_order_id": self.take_profit_order.client_order_id
                },
            "stop_loss": {
                "stop_price": self.stop_loss_order.stop_price,
                "client_order_id": self.stop_loss_order.client_order_id
                }
        }


@dataclass
class Trade:
    trade_id: str
    time: datetime
    symbol: str
    qty: float
    entry: float
    stop: float
    target: float
    status: str
    risk_usd: float
    strategy: Optional[str] = None
    avg_price_entry: Optional[float] = None
    avg_price_stop: Optional[float] = None
    avg_price_take_profit: Optional[float] = None
    profit_loss: Optional[float] = None
    commission: Optional[float] = None


class DataFeed:
    def __init__(self, engine):
        self.engine = engine

    def get_candles(self):
        pass


class Broker(ABC):
    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def market_is_open(self) -> bool:
        """
        A function that checks if market is open

        Returns:
            bool: True if market open
            bool: False of market closed
        """
        pass

    @abstractmethod
    def get_assets(self) -> List[Asset]:
        """
        A function that retrieves all assets from broker

        Returns:
            List[Stock]: A list of Asset objects with properties for each asset
        """
        pass

    @abstractmethod
    def in_position(self, ticker: str) -> bool:
        """
        A function that checks if supplied symbol has open positions

        Args:
            ticker (str): The Symbol of the ticker to check

        Returns:
            bool: True if open positions found
            bool: False if no open positions found
        """
        pass

    @abstractmethod
    def check_account_balance(self) -> float:
        """
        Retrieves the account balance as a float.
        In this case, account balance refers to "Non-Marginable Buying Power"
        This number may be lower than account equity if funds are settling

        Returns:
            float: The current account balance as a float value.
        """
        pass

    @abstractmethod
    def check_account_equity(self) -> float:
        """
        Retrieves the account equity as a float.
        This is the entire balance regardless including open positions and
        unsettled margin funds

        Returns:
            float: The current account equity as a float value.
        """
        pass

    @abstractmethod
    def check_existing_orders(self, ticker: str) -> List[str]:
        """
        Retrieves and prints information about pending orders for a given ticker symbol.

        Args:
            ticker (str): The ticker symbol for which to check pending orders.

        Returns:
            List[str]: A list of order IDs for pending orders.
        """
        pass

    @abstractmethod
    def submit_order(self, order) -> dict:
        """
        Submits an order to the API for execution.

        Args:
            order (Order): The order to be submitted.

        Returns:
            dict: The json response of the order as a dict. Will be formatted with bracket orders for stop and take profit as a list of those orders under the key "legs"

        Logs:
            Prints order to be submitted: "ORDER TO SUBMIT: (Order)
            Prints order response from broker: "ORDER RESPONSE: (dict response)
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """
        Cancels an order with the given order ID.

        Args:
            order_id (str): The ID of the order to be cancelled.

        Returns:
            None
        """
        pass


class Strategy(ABC):
    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def onData(self, candle: Candle, broker: Broker):
        """
        engine will call onData every time a new candle is reported
        This function is called on every new candle object.
        """
        pass


class Engine:
    def __init__(self):
        self.asset = Asset()
        self.datasource = DataFeed(self)
        self.strategy = Strategy(self)
        self.broker = Broker(self)

    def set_log_level(self, log_level: str) -> None:
        set_logs(log_level)

    def run():
        pass
