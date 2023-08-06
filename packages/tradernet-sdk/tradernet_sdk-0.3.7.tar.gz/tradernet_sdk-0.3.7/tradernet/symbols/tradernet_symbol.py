"""
TraderNet market data
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pandas import DataFrame, to_datetime

from tradernet.client import TraderNetAPI
from tradernet.symbols.base_market_symbol import BaseMarketSymbol


class TraderNetSymbol(BaseMarketSymbol):
    """
    Acquiring and processing data from TraderNet.

    Parameters
    ----------
    symbol : str
        A symbol name on a remote service.
    start : datetime
        The first date of the period market data to be acquired within.
    end : datetime
        The last date of the period.

    Attributes
    ----------
    symbol : str
        A symbol name on a remote service.
    start : datetime
        The first date of the period market data to be acquired within.
    end : datetime
        The last date of the period.
    market_data : pandas.DataFrame
        A dataframe containing timeseries of candles: open, close, high, low.
    timeframe : int
        Timeframe of candles in seconds. Default is 86400 corresponding to day
        candles.
    """
    __slots__ = ('timeframe',)

    def __init__(
        self,
        symbol: str,
        api: TraderNetAPI | None = None,
        start: datetime = datetime(1970, 1, 1),
        end: datetime = datetime.utcnow()
    ) -> None:
        super().__init__(symbol, api, start, end)
        self.timeframe = 86400

    def __parse_candles(self, candles: dict[str, Any]) -> DataFrame:
        timestamps = \
            [*map(datetime.fromtimestamp, candles['xSeries'][self.symbol])]
        volumes = candles['vl'][self.symbol]
        data = DataFrame(
            candles['hloc'][self.symbol],
            columns=['high', 'low', 'open', 'close']
        )
        data = data.assign(volume=volumes)
        data = data.assign(date=to_datetime(timestamps).round('D'))
        return data

    def get_data(self) -> None:
        if not self.api or not isinstance(self.api, TraderNetAPI):
            self.api = TraderNetAPI()

        candles = self.api.get_candles(
            self.symbol, timeframe=self.timeframe,
            start=self.start, end=self.end
        )

        if 'hloc' in candles:
            data = self.__parse_candles(candles)
        else:
            return
        self.market_data = data.set_index('date').sort_index()
