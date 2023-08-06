from __future__ import annotations

from collections import OrderedDict
from logging import getLogger
from typing import Any
from urllib.parse import quote

from requests import Response, Session as HTTPSession

from tradernet.common.string_utils import StringUtils


class NetUtils(StringUtils):
    __slots__ = ('session', 'timeout', 'logger')

    def __init__(self) -> None:
        self.session: HTTPSession | None = None
        self.timeout = 300
        self.logger = getLogger(self.__class__.__name__)

    def http_build_query(self, dictionary: dict[str, Any]) -> str:
        """
        Full analogue of the PHP function `http_build_query`.

        Parameters
        ----------
        dictionary : dict[str, Any]
            Any dictionary.

        Returns
        -------
        str
            The query built.
        """
        result = OrderedDict()

        for key, value in dictionary.items():
            if isinstance(value, list):
                for list_key, list_value in self.flatten_list(value).items():
                    result[f'{key}{list_key}'] = list_value

            elif isinstance(value, dict):
                for dict_key, dict_value in self.flatten_dict(value).items():
                    result[f'{key}{dict_key}'] = dict_value

            else:
                result[key] = value

        return self.str_from_dict(self.apply_to_dict(
            lambda va: quote(va) if isinstance(va, str) else va, result
        ))

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: str | dict[str, Any] | None = None,
        data: bytes | str | dict[str, Any] | None = None
    ) -> Response:
        if not self.session:
            self.session = HTTPSession()

        response = self.session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            timeout=self.timeout or None
        )
        self.logger.debug('Response url %s', response.url)

        try:
            response.raise_for_status()
        except Exception:
            self.logger.exception('Got request exception')
            raise

        return response
