from .models import *
from .logger import logger
from typing import Optional
from datetime import datetime


class PrintStrategy(Strategy):
    def __init__(self, engine:Engine, time_int:int, time_period:str, start:Optional[datetime] = None, end:Optional[datetime] = None, limit:Optional[int] = None):
        super().__init__(engine)
        self.time_int = time_int
        self.time_period = time_period
        self.start = start
        self.end = end
        self.limit = limit

        self.indicators = [
            "heikin_ashi",
            "bars_down"
        ] 

    def onData(self, candle:Candle):
        """
        This function is called by run.py on every new candle to DB
        Timeframe is determined by config above
        """
        logger.debug("---- SYMBOL:")
        logger.debug(self.engine.asset.symbol)
        logger.debug("---- BROKER:")
        logger.debug(self.engine.broker)
        logger.debug("---- CANDLE:")
        logger.debug(candle)
        logger.debug("--------------------")

