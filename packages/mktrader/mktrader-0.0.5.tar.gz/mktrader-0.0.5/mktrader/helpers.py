from .logger import logger
from .models import Order, Candle
from datetime import datetime, timedelta
from typing import List
import copy


def get_next_run_time(date_time: datetime, num: int, period: str) -> datetime:
    """
    Calculates the next run time based on the given time period and number.
    Args:
        num (int): Number to be used to calculate the next run time.
        period (str): Time period for which the next run time needs to be calculated. Valid values are 'min' and 'hour'.
    Returns:
        datetime: The next run time.
            IE: if strategy is set to hourly, and it's 3:12pm this would return 4:00 as the next run time.
    Raises:
        None
    """
    logger.debug(f"Time: {date_time}")
    if period == 'min':
        dt = date_time + timedelta(minutes=1)
        hour = dt.hour
        day = dt.day
        next_minute = int(dt.minute)
        while next_minute % num != 0:
            next_minute = next_minute + 1
            if next_minute == 60:
                next_minute = 0
                hour = hour + 1
        if hour == 24:
            hour = 0
            day = day + 1
        dt = dt.replace(day=day, hour=hour, minute=next_minute, second=00, microsecond=00)
        logger.debug(f"NEXT RUN: {dt.hour}:{dt.minute}")
    elif period == 'hour':
        dt = date_time + timedelta(hours=1)
        day = dt.day
        next_hour = int(dt.hour)
        while next_hour % num != 0:
            next_hour = next_hour + 1
            if next_hour == 24:
                next_hour = 0
                day = day + 1
        dt = dt.replace(day=day, hour=next_hour, minute=00, second=00, microsecond=00)
        logger.debug(f"NEXT RUN: {dt.hour}:{dt.minute}")
    else:
        logger.debug("Invalid Time Period...")
        return None
    logger.info("\n--------------------------------------")
    return dt


def orderDict_to_Order(orders_dict: dict) -> List[Order]:
    """
    Convert dict (order) to Order object using dictionary comprehension for matching keys
    """
    orders = []
    for order_item in orders_dict:
        logger.debug(f"ORDER-DICT: {order_item}")
        order_kwargs = {k: v for k, v in order_item.items() if k in Order.__annotations__}
        # Use the unpacking operator to pass the order_kwargs dictionary as keyword arguments to create a new Order object
        order = Order(**order_kwargs)
        logger.debug(f"ORDER OBJECT CREATED: {vars(order)}")
        orders.append(order)
    logger.debug(f"ORDER OBJECTS LIST FINALIZED: {orders}")
    return orders


def process_orders(message: dict) -> List[Order]:
    """
    This takes alpaca API order response as a dict and processes it into a list of Order objects
    Helpful for inserting into DB for tracking orders.
    """
    logger.debug(f"ORDER TO PROCESS: {message}")
    logger.debug(f"ORDER TO PROCESS TYPE = {type(message)}")

    orders = []

    if "legs" in message and isinstance(message["legs"], (list, dict)):
        logger.debug("MESSAGE HAS LEGS, PROCESSING...")
        for leg in message["legs"]:
            orders.append(leg)
            logger.debug("APPENDING LEGS TO ORDERS")

        # Create a copy of the message and remove the legs from the copy
        message_copy = copy.deepcopy(message)
        message_copy["legs"] = None
        orders.append(message_copy)
    else:
        orders.append(message)
    logger.debug(f"ORDERS LIST: {orders}")

    order_objects = orderDict_to_Order(orders)
    logger.debug(f"ORDER OBJECTS PROCESSED: {order_objects}")
    return order_objects


def log_candle_info(candle: Candle):
    logger.info("\n--------------------------------------")
    logger.info(f"Candle Time: {candle.date}")
    logger.info(f"NEW CANDLE ---> {candle.ticker} O:{candle.open:.2f} H:{candle.high:.2f} L:{candle.low:.2f} C:{candle.close:.2f} - Stop:{candle.recent_low:.2f} - BarsDN:{candle.bars_dn}")
