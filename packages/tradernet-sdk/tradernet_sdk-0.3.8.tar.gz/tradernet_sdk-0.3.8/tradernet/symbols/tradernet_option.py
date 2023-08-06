from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from tradernet.symbols.base_option_symbol import BaseOptionSymbol
from tradernet.symbols.option_properties import OptionProperties


class TraderNetOption(BaseOptionSymbol):
    @staticmethod
    def decode_notation(symbol: str) -> OptionProperties:
        """
        +AAPL.18MAR2022.P150 -> (AAPL, '', -1, 150, 2022-03-18, 18MAR2022)
        """
        assert symbol.startswith('+'), \
            'Entered symbol is not a TraderNet option!'

        name_sections = symbol[1:].split('.')  # removing leading '+'

        for idx, section in enumerate(name_sections):
            try:
                expiration = TraderNetOption.decode_date(section)
                break
            except ValueError:
                continue
        else:
            raise RuntimeError('Entered symbol is not a TraderNet option!')

        # `idx` is the index of the expiration date
        assert 1 < len(name_sections[idx:]) < 4, \
            f'Entered symbol {symbol} is not a TraderNet option!'

        symbolic_expiration = name_sections[idx]
        # Everything before expiration is ticker
        ticker = '.'.join(name_sections[:idx])
        # The TraderNet option notation has no location
        location = ''

        if name_sections[idx + 1][0] == 'P':
            right = -1
        elif name_sections[idx + 1][0] == 'C':
            right = 1
        else:
            raise RuntimeError('Entered symbol is not a TraderNet option!')

        strike = Decimal('.'.join(name_sections[idx + 1:])[1:])

        return OptionProperties(
            ticker, location, right, strike, expiration, symbolic_expiration
        )

    @staticmethod
    def encode_date(conventional_date: str | date | datetime) -> str:
        if isinstance(conventional_date, str):
            conventional_date = date.fromisoformat(conventional_date)

        return conventional_date.strftime('%d%b%Y').upper()

    @staticmethod
    def decode_date(symbolic_date: str) -> date:
        return datetime.strptime(symbolic_date, '%d%b%Y').date()
