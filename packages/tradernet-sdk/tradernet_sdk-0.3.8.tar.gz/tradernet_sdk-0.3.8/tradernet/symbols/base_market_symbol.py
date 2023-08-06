from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime, date
from logging import getLogger

from numpy import (
    array, ndarray, diff, float64, datetime64, isfinite, isnan, log
)
from numpy.typing import NDArray
from pandas import DataFrame, to_datetime, melt

from tradernet.client import TraderNetAPI


def np_to_date(value: datetime64) -> date:
    dt = datetime.fromtimestamp(value.astype('O')/1e9)
    return date(dt.year, dt.month, dt.day)


class BaseMarketSymbol(metaclass=ABCMeta):
    """
    An abstract base class to get market data containing methods for their
    processing.

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
    api : API class instance, optional
        API is to be used to get market data.
    start : datetime
        The first date of the period market data to be acquired within.
    end : datetime
        The last date of the period.
    market_data : pandas.DataFrame
        A dataframe containing timeseries of candles: open, close, high, low.
    logger : Logger
        Saving info and debugging.
    """
    __slots__ = (
        'symbol',
        'api',
        'start',
        'end',
        'logger',
        'market_data'
    )

    def __init__(
        self,
        symbol: str,
        api: TraderNetAPI | None = None,
        start: datetime = datetime(1970, 1, 1),
        end: datetime = datetime.utcnow()
    ) -> None:
        self.symbol = symbol
        self.api = api

        # Dates interval
        self.start = start
        self.end = end

        self.logger = getLogger(self.__class__.__name__)

        self.market_data = DataFrame()

    def ffill(self, freq: str = '1D') -> None:
        today = date.today()
        try:
            self.market_data.loc[today]
        except KeyError:
            self.market_data = self.market_data.reindex(
                [*self.market_data.index.values, today]
            )

        self.market_data = self.market_data.reindex(
            to_datetime(self.market_data.index.values)
        )
        filled = self.market_data.resample(freq).ffill()
        filled = filled.reindex([*map(np_to_date, filled.index.values)])
        self.market_data = filled.ffill()

    def returns(self, kind: str = 'percent') -> NDArray[float64]:
        """
        Computing returns from market data.

        Parameters
        ----------
        kind : str
            A kind of returns. Allowed values are `percent` and `log` meaning
            per cent to previous close or natural logarithm of closes ratio.

        Returns
        -------
        result : array_like
            Symbol returns free of null values.
        """
        if 'close' not in self.market_data.columns:
            return array([])
        close_prices = self.market_data.close.values
        if kind == 'percent':
            data = diff(close_prices)/close_prices[:-1]
        elif kind == 'log':
            data = log(close_prices[1:]/close_prices[:-1])
        else:
            raise RuntimeError('Invalid return kind')
        # Filtering infinities out
        data = data[isfinite(data)]
        # Filtering non-numbers
        return data[~isnan(data)]

    def gaps(self, kind: str = 'percent') -> NDArray[float64]:
        """
        Computing gaps from market data.

        Parameters
        ----------
        kind : str
            A kind of returns. Allowed values are `percent` and `log` meaning
            per cent to previous close or natural logarithm of closes ratio.

        Returns
        -------
        result : array_like
            Symbol gaps free of null values.

        Notes
        -----
        Gap is a distance from the close price to the open price next business
        day.
        """
        columns = self.market_data.columns
        if 'open' not in columns or 'close' not in columns:
            return array([])
        open_prices = self.market_data.open.values
        close_prices = self.market_data.close.values
        if kind == 'percent':
            data = open_prices[1:]/close_prices[:-1] - 1
        elif kind == 'log':
            data = log(open_prices[1:]/close_prices[:-1])
        else:
            raise RuntimeError('Invalid return kind')
        # Filtering infinities out
        data = data[isfinite(data)]
        # Filtering non-numbers
        return data[~isnan(data)]

    def last_price(self) -> float | None:
        """
        Extracts the last non-null price from market data, either at the market
        open, or at close.

        Returns
        -------
        float, optional
            The last price if there is one.
        """
        if self.market_data.empty:
            self.logger.warning('No last price: market data is empty')
            return None

        # Melting all prices, one after another
        melted_table = melt(
            self.market_data[['open', 'close']].reset_index(),
            id_vars=['date'], var_name='moment', value_name='price'
        )
        # Creating a united dateless sequence of prices
        price_sequence = melted_table.set_index('date').sort_values(
            'moment', ascending=False   # opening prices first, then closing
        ).sort_index()['price'].values  # sorting dates, extracting prices

        if not isinstance(price_sequence, ndarray):
            # Something went wrong, the returned sequence is not a numpy array
            self.logger.warning('Failed to melt data')
            return None

        # Throwing away nulls
        existing_prices = price_sequence[~isnan(price_sequence)]
        if existing_prices.size == 0:
            self.logger.warning('All prices found are null')
            return None

        price = existing_prices[-1]  # Behold, the last price!
        self.logger.debug('Last price of %s is %s', self.symbol, price)
        return price

    @abstractmethod
    def get_data(self) -> None:
        """
        Abstract method acquiring data and assigning
        BaseMarketSymbol.market_data to them.
        """
