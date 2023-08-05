# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from contextlib import ContextDecorator
from contextvars import ContextVar
from typing import Any

from cbra.core.conf import settings
from .translation import Translation


DEFAULT_LANGUAGE: str = 'en'
catalogs: dict[str | None, Translation] = {
    None: Translation('en')
}
current_language: ContextVar[str] = ContextVar("Language", default=DEFAULT_LANGUAGE)


class LanguageContext(ContextDecorator):
    __module__: str = 'cbra.core.translation'
    _deactivate: bool
    _old_language: str | None = None

    @staticmethod
    def catalog() -> Translation:
        l = LanguageContext.get()
        c = catalogs.get(l)
        if c is None:
            c = catalogs[c] = Translation(l, localedirs=settings.LOCALE_PATHS) # type: ignore
        return c

    @staticmethod
    def get() -> str:
        return current_language.get() or DEFAULT_LANGUAGE

    @staticmethod
    def gettext(message: str) -> str:
        c = LanguageContext.catalog()
        return c.gettext(message)

    @staticmethod
    def ngettext(singular: str, plural: str, number: int) -> str:
        c = LanguageContext.catalog()
        return c.ngettext(singular, plural, number)

    @staticmethod
    def activate(language: str | None) -> None:
        current_language.set(language or DEFAULT_LANGUAGE)

    def __init__(self, language: str | None, deactivate: bool = False):
        self._deactivate = deactivate
        self.language = language

    def __enter__(self):
        self._old_language = self.get()
        if self.language is not None:
            self.activate(self.language)

    def __exit__(self, *args: Any, **kwargs: Any):
        if self._old_language is not None:
            self.activate(self._old_language)
