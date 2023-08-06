from .models import Engine, Candle
from .logger import logger
from . import indicators, helpers
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque


@dataclass
class Live_Websocket(Engine):
    """
    Websocket function.

    - requests history of bars in proper timeframe
    - Listens to 1 minute websocket connection.
    - Stores incoming bars and resamples to the required timeframe
    - Appends new candle to candles list
    ---
    - applies indicators from strategy
    - pulls out latest candle
    - passes candle to strategy.onData function
    """

    previous_bar = None
    candles = []
    minute_candle_deque = deque([])

    def on_candle(self, candle: Candle):
        self.minute_candle_deque.append(candle)
        next_candle_start = helpers.get_next_run_time(date_time=candle.date, num=self.strategy.time_int, period=self.strategy.time_period)

        last_current_candle_bar = next_candle_start - timedelta(minutes=1)
        if candle.date == last_current_candle_bar:
            open = self.minute_candle_deque[0].open
            high = max(c.high for c in self.minute_candle_deque)
            low = min(c.low for c in self.minute_candle_deque)
            close = self.minute_candle_deque[-1].close
            volume = sum(c.volume for c in self.minute_candle_deque)

            new_candle = Candle(self.minute_candle_deque[0].ticker, self.minute_candle_deque[0].date, open, high, low, close, volume)

            logger.info(new_candle)
            self.candles.append(new_candle)
            # remove the used candles from the deque
            self.minute_candle_deque.clear()

            # INDICATORS
            indicated_candles = indicators.add_indicators(self.strategy, self.candles)
            # PROCESS
            latest_candle = indicated_candles[-1]
            if not self.broker.market_is_open(latest_candle):
                if self.strategy.extended_hours is False:
                    logger.info("Market Closed..")
                    return
                elif self.strategy.extended_hours is True:
                    logger.info("Extended Hours Session..")
            if self.previous_bar is None or latest_candle.date > self.previous_bar.date:
                helpers.log_candle_info(candle=latest_candle)
                self.strategy.onData(candle=latest_candle, broker=self.broker)
                self.previous_bar = latest_candle
            else:
                logger.debug("BAR EXISTS, SKIPPING")

    def run(self):
        self.candles = self.datasource.get_candles()
        logger.debug(self.candles)

        """We may have an incomplete current candle. We need to scrap it from
        the history if it exists and grab any missing data needed to fill the
        minute_candle_deque so our new candle calculations will be complete."""

        next_candle_start = helpers.get_next_run_time(
                date_time=datetime.utcnow(),
                num=self.strategy.time_int,
                period=self.strategy.time_period)
        if self.strategy.time_period == "min":
            in_process_candle_start = next_candle_start - timedelta(minutes=self.strategy.time_int)
        elif self.strategy.time_period == "hour":
            in_process_candle_start = next_candle_start - timedelta(hours=self.strategy.time_int)
        logger.debug(f"IN PROCESS CANDLE TO DELETE [TIME]: {in_process_candle_start}")
        for candle in self.candles:
            if candle.date >= in_process_candle_start:
                del self.candles[self.candles.index(candle)]
        logger.debug("LIST UPDATED TO REMOVE ANY IN-PROCESS CANDLES:")
        logger.debug(self.candles)

        """Now we need to get 1-minute candles and pass them to the minute_candle_list
        before we start getting real-time 1-minute candles"""

        catch_up_minute_candles = self.datasource.get_candles(minute_catch_up=in_process_candle_start)
        logger.debug("CATCH UP MINUTE CANDLES:")
        logger.debug(catch_up_minute_candles)
        # Add them to the deque to be processed
        for catch_up_candle in catch_up_minute_candles:
            self.minute_candle_deque.append(catch_up_candle)
        # Now start getting live candles
        self.datasource.get_live_candles()
