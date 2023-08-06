from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, ClassVar

from tradernet.core import TraderNetCore


class Trading(TraderNetCore):
    DURATION: ClassVar[dict[str, int]] = {
        'day': 1,  # The order will be valid until the end of the trading day.
        'ext': 2,  # Extended day order.
        'gtc': 3   # A.k.a. "Good Till Cancelled"
    }

    def open_security_session(
        self,
        *args: bool,
        **kwargs: bool
    ) -> Callable[[str], dict[str, Any]]:
        """
        Opening a new security session.

        Returns
        -------
        result : Callable[[str], dict]
            A function that accepts a security code and returns an answer
            containing login information.

        Notes
        -----
        Use it as follows:
        >>> trade = Trading.from_config('tradernet.ini')
        >>> opening = trade.open_security_session(False, True)  # Send to app
        >>> opening(123456)  # Push you received
        """
        self.send_security_sms(*args, **kwargs)
        return lambda token: self.open_with_sms(str(token))

    def buy(
        self,
        symbol: str,
        quantity: int = 1,
        price: float = 0.0,
        duration: str = 'day',
        use_margin: bool = True
    ) -> dict[str, Any]:
        """
        Placing a new buy order.

        Parameters
        ----------
        symbol : str
            TraderNet symbol.
        quantity : int, optional
            Units of the symbol, by default 1.
        price : float, optional
            Limit price, by default 0.0 that means market order.
        duration : str, optional
            Time to order expiration, by default 'day'.
        use_margin : bool, optional
            If margin credit might be used, by default True.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        cmd = 'putTradeOrder'
        params = {
            'instr_name': symbol,
            'action_id': 2 if use_margin else 1,
            'order_type_id': 2 if price else 1,
            'qty': quantity,
            'limit_price': price,
            'expiration_id': self.DURATION[duration.lower()]
        }
        return self.authorized_request(cmd, params, version=2)

    def sell(
        self,
        symbol: str,
        quantity: int = 1,
        price: float = 0.0,
        duration: str = 'day',
        use_margin: bool = True
    ) -> dict[str, Any]:
        """
        Placing a new sell order.

        Parameters
        ----------
        symbol : str
            TraderNet symbol.
        quantity : int, optional
            Units of the symbol, by default 1.
        price : float | None, optional
            Limit price, by default 0.0 that means market order.
        duration : str, optional
            Time to order expiration, by default 'day'.
        use_margin : bool, optional
            If margin credit might be used, by default True.
        """
        cmd = 'putTradeOrder'
        params = {
            'instr_name': symbol,
            'action_id': 4 if use_margin else 3,
            'order_type_id': 2 if price else 1,
            'qty': quantity,
            'limit_price': price,
            'expiration_id': self.DURATION[duration.lower()]
        }
        return self.authorized_request(cmd, params, version=2)

    def stop(self, symbol: str, price: float) -> dict[str, Any]:
        """
        Placing a new stop order on a certain open position.

        Parameters
        ----------
        symbol : str
            TraderNet symbol.
        price : float
            Stop price.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        cmd = 'putStopLoss'
        params = {
            'instr_name': symbol,
            'stop_loss': price
        }
        return self.authorized_request(cmd, params, version=2)

    def trailing_stop(self, symbol: str, percent: int = 1) -> dict[str, Any]:
        """
        Placing a new trailing stop order on a certain open position.

        Parameters
        ----------
        symbol : str
            TraderNet symbol.
        percent : int, optional
            Stop loss percentage, by default 1.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        cmd = 'putStopLoss'
        params = {
            'instr_name': symbol,
            'stop_loss_percent': percent,
            'stoploss_trailing_percent': percent
        }
        return self.authorized_request(cmd, params, version=2)

    def take_profit(self, symbol: str, price: float) -> dict[str, Any]:
        """
        Placing a new take profit order on a certain open position.

        Parameters
        ----------
        symbol : str
            TraderNet symbol.
        price : float
            Take profit price.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        cmd = 'putStopLoss'
        params = {
            'instr_name': symbol,
            'take_profit': price
        }
        return self.authorized_request(cmd, params, version=2)

    def cancel(self, order_id: int) -> dict[str, Any]:
        """
        Cancelling an order.

        Parameters
        ----------
        order_id : int
            Order ID.
        """
        cmd = 'delTradeOrder'
        params = {'order_id': order_id}
        return self.authorized_request(cmd, params, version=2)

    def get_placed(self, active: bool = True) -> dict[str, Any]:
        """
        Getting a list of orders in the current period.

        Parameters
        ----------
        active : bool, optional
            Show only active orders.

        Returns
        -------
        result : dict
            A dictionary of orders.

        Notes
        -----
        https://tradernet.ru/tradernet-api/orders-get-current-history
        """
        cmd = 'getNotifyOrderJson'
        params = {'active_only': int(active)}
        return self.authorized_request(cmd, params)

    def get_historical(
        self,
        start: datetime = datetime(1970, 1, 1),
        end: datetime = datetime.utcnow()
    ) -> dict[str, Any]:
        """
        Getting a list of orders in the period.

        Parameters
        ----------
        start : datetime, optional
            Period start date.
        end : datetime, optional
            Period end date.

        Returns
        -------
        result : dict
            A dictionary of orders.

        Notes
        -----
        https://tradernet.ru/tradernet-api/get-orders-history
        """
        cmd = 'getOrdersHistory'
        params = {
            'from': start.strftime('%Y-%m-%dT%H:%M:%S'),
            'till': end.strftime('%Y-%m-%dT%H:%M:%S')
        }
        if not self._session_id:
            self.get_authorized()
        return self.plain_request(cmd, params)
