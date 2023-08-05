from typing import List
from .models import Candle
from .logger import logger

"""
This file is only for functions that take lists of candle objects and runs indicators on them,
always returning the same list with added properties.

NOTE: Lists MUST be sorted by date ASC, with index[0] being the OLDEST candle

"""


def add_indicators(strategy, candles: List[Candle]) -> List[Candle]:
    """
    Args: List of Candles sorted ASC
    Returns: List of Candles with new properties added
    Config: Add the names of the indicators to the strategy.
    Note: Runs prior to get_data since get_data only takes 1 candle. Indicators need all.
    """

    candles = sorted(candles, key=lambda x: x.date)  # sort by date ascending

    if "heikin_ashi" in strategy.indicators:
        logger.debug("Converting Candles to Heiken-Ashi")
        candles = heikinashi(candles)

    if "bars_down" in strategy.indicators:
        logger.debug("Adding Bars Down Counts")
        candles = bars_down(candles=candles, property_name="high")

    if "recent_low" in strategy.indicators:
        logger.debug("Adding Recent Lows")
        candles = recent_low(candles=candles, num_values=strategy.stop_lookback)

    return candles


def heikinashi(candles: List[Candle]) -> List[Candle]:
    """
        Formula:
        ha_open = (ha_open(-1) + ha_close(-1)) / 2
        ha_high = max(hi, ha_open, ha_close)
        ha_low = min(lo, ha_open, ha_close)
        ha_close = (open + high + low + close) / 4
    """
    ha_candles = []
    previous_candle = None
    for count, candle in enumerate(candles):
        if count == 0:
            candle.ha_open = (candle.open + candle.close) / 2
        else:
            candle.ha_open = (previous_candle.ha_open + previous_candle.ha_close) / 2
        candle.ha_close = (candle.open + candle.high + candle.low + candle.close) / 4
        candle.ha_high = max(candle.high, candle.ha_open, candle.ha_close)
        candle.ha_low = min(candle.low, candle.ha_open, candle.ha_close)

        ha_candle = Candle(
            ticker=candle.ticker,
            date=candle.date,
            open=candle.ha_open,
            high=candle.ha_high,
            low=candle.ha_low,
            close=candle.ha_close,
            volume=candle.volume
            )
        ha_candles.append(ha_candle)
        previous_candle = candle
    return ha_candles


def bars_down(candles: List[Candle], property_name: str = 'high') -> List[Candle]:
    """
    Calculates the number of consecutive bars with lower or equal highs, lows, opens, or closes
    for each candle in the given list of candles.

    Args:
        candles (List[Candle]): A list of Candle objects.
        property_name (str): The name of the property to use for the calculations. Default is 'high'.
            Possible values are 'open', 'high', 'low', or 'close'.

    Returns:
        List[Candle]: The original list of candles with an additional property 'bars_dn'
        added to each candle, representing the number of consecutive bars with lower or equal
        highs, lows, opens, or closes, based on the specified property_name.
    """

    for i, candle in enumerate(candles):
        if not hasattr(candle, property_name):
            raise ValueError(f"Candle objects do not have property '{property_name}'.")
        property_value = getattr(candle, property_name)
        if i == 0:
            candle.bars_dn = 0
        else:
            prev_candle = candles[i - 1]
            prev_property_value = getattr(prev_candle, property_name)
            if property_value <= prev_property_value:
                candle.bars_dn = prev_candle.bars_dn + 1
            else:
                candle.bars_dn = 0
    return candles


def recent_low(candles: List[Candle], num_values: int) -> List[Candle]:
    """
    Find the recent lowest low in the last `num_values` number of bars in a list of Candle objects.

    Args:
        candles (list): List of Candle objects.
        num_values (int): Number of bars to look back for finding the lowest low.

    Returns:
        list: List of Candle objects with the recent_low property updated.
    """
    # if num_values == 0:
    #     raise ValueError("stop_lookback must be a minimum of 1")

    for i in range(len(candles)):
        # Calculate the starting index for the sublist
        start_index = max(0, i - num_values)
        # Use a list comprehension to get the low values of the previous candles
        prev_lows = [candle.low for candle in candles[start_index:i+1]]
        # Find the lowest low value
        lowest_low = min(prev_lows) if prev_lows else candles[i].low
        # Update the recent_low property for the current candle
        candles[i].recent_low = lowest_low

    return candles
