from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar
from string import ascii_uppercase, digits

from tradernet.symbols.base_option_symbol import BaseOptionSymbol
from tradernet.symbols.option_properties import OptionProperties


class DasOption(BaseOptionSymbol):
    NUMCHAR: ClassVar[str] = f'{digits}{ascii_uppercase}'

    @staticmethod
    def decimal_to_base(number: int, base: int) -> str:
        if number < base:
            return DasOption.NUMCHAR[number]
        return DasOption.decimal_to_base(number // base, base) \
            + DasOption.NUMCHAR[number % base]

    @staticmethod
    def starting_year() -> int:
        return (date.today().year - 10) // 20 * 20 + 10

    @staticmethod
    def decode_date(symbolic_date: str) -> date:
        assert len(symbolic_date) == 3, 'Invalid date format'

        year = DasOption.starting_year() + int(symbolic_date[0], 20)
        month = int(symbolic_date[1], 16)
        day = int(symbolic_date[2], 32)

        return date(year, month, day)

    @staticmethod
    def decode_notation(symbol: str) -> OptionProperties:
        """
        +AAPL*C3I150.US -> (AAPL, US, -1, 150, 2022-03-18, C3I)
        """
        put_index = symbol.find('*')
        call_index = symbol.find('^')

        assert symbol[0] == '+' and (put_index != -1 or call_index != -1), \
            'Entered symbol is not a DAS option!'
        # Index-separator
        if call_index != -1:
            idx = call_index
            right = 1
        else:
            idx = put_index
            right = -1
        # Index following ticker
        ticker = symbol[1:idx]
        symbolic_expiration = symbol[idx + 1:idx + 4]
        expiration = DasOption.decode_date(symbolic_expiration)

        tail = symbol[idx + 4:].split('.')
        try:
            _ = int(tail[1])
            strike = Decimal('.'.join(tail[0:2]))
            location: str | None = '.'.join(tail[2:])
        except (IndexError, ValueError):
            strike = Decimal(tail[0])
            location = '.'.join(tail[1:])

        if not location:
            location = None
        return OptionProperties(
            ticker, location, right, strike, expiration, symbolic_expiration
        )

    @staticmethod
    def encode_date(conventional_date: str | date | datetime) -> str:
        if isinstance(conventional_date, str):
            conventional_date = date.fromisoformat(conventional_date)

        year = DasOption.decimal_to_base(
            conventional_date.year - DasOption.starting_year(), 20
        )
        month = DasOption.decimal_to_base(
            conventional_date.month, 16
        )
        day = DasOption.decimal_to_base(
            conventional_date.day, 32
        )

        return f'{year}{month}{day}'
