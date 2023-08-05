# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
import urllib.request
from typing import NamedTuple

import fastapi
import fastapi.params

from .idependant import IDependant
from .malformedheader import MalformedHeader


ACCEPT_LANGUAGE_HEADER_MAX_LENGTH: int = 500


class RequestLanguage(IDependant):
    __module__: str = 'cbra.types'
    # Format of Accept-Language header values. From RFC 9110 Sections 12.4.2 and
    # 12.5.4, and RFC 5646 Section 2.1.
    pattern: re.Pattern[str] = re.compile(
        r"""
            # "en", "en-au", "x-y-z", "es-419", "*"
            ([A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*|\*)
            # Optional "q=1.00", "q=0.8"
            (?:\s*;\s*q=(0(?:\.[0-9]{,3})?|1(?:\.0{,3})?))?
            # Multiple accepts per header.
            (?:\s*,\s*|$)
        """,
        re.VERBOSE,
    )

    class AcceptedLanguage(NamedTuple):
        code: str
        weight: float


    @classmethod
    def parse_language(cls, language: str) -> AcceptedLanguage:
        if ';' not in language:
            return cls.AcceptedLanguage(language, 1.0)
        else:
            language, sep, weight = language.partition(';q=')
            if sep != ';q=': # pragma: no cover
                raise MalformedHeader
            try:
                return cls.AcceptedLanguage(language, float(weight))
            except (ValueError, TypeError): # pragma: no cover
                raise MalformedHeader

    def __init__(
        self,
        accept_language: str | None = fastapi.Header(
            default=None,
            alias='Accept-Language',
            title="Language(s)",
            description=(
                "The `Accept-Language` request HTTP header indicates the natural "
                "language and locale that the client prefers. The server uses "
                "content negotiation to select one of the proposals and informs "
                "the client of the choice with the `Content-Language` response "
                "header. Browsers set required values for this header according "
                "to their active user interface language."
            )
        )
    ) -> None:
        # If accept_language is a header instance, this was not invoked through
        # FastAPI dependency injection.
        if isinstance(accept_language, fastapi.params.Header):
            accept_language = None
        self.languages = []
        if accept_language is not None\
        and len(accept_language) <= ACCEPT_LANGUAGE_HEADER_MAX_LENGTH:
            if not self.pattern.match(accept_language):
                raise MalformedHeader
            self.languages = [
                self.parse_language(x)
                for x in urllib.request.parse_http_list(accept_language)
                if x != '*'
            ]
            self.languages = list(sorted(self.languages, key=lambda x: -x.weight))
        if not self.languages:
            self.languages.append(self.AcceptedLanguage('en', 1.0))

    def select(self, available: set[str], default: str = 'en') -> str:
        """Select a language based on the given available languages."""
        available = {str.lower(x) for x in available}
        for language in self.languages:
            if str.lower(language.code) not in available:
                continue
            break
        else:
            language = self.AcceptedLanguage(default, 1.0) 
        return language.code