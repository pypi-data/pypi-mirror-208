# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import gettext
from typing import Callable


class TranslationCatalog:
    __module__: str = 'cbra.core.translation'
    _catalogs: list[dict[str, str]]
    _plurals: list[Callable[[int], int]]

    def __init__(self, trans: gettext.NullTranslations | None = None):
        self._catalogs = [trans._catalog.copy()] if trans else [{}] # type: ignore
        self._plurals = [trans.plural] if trans else [lambda n: int(n != 1)] # type: ignore

    def __getitem__(self, key: str) -> str:
        for cat in self._catalogs:
            try:
                return cat[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key: str, value: str):
        self._catalogs[0][key] = value

    def __contains__(self, key: str):
        return any(key in cat for cat in self._catalogs)

    def items(self):
        for cat in self._catalogs:
            yield from cat.items()

    def keys(self):
        for cat in self._catalogs:
            yield from cat.keys()

    def update(self, trans: gettext.NullTranslations):
        # Merge if plural function is the same, else prepend.
        for cat, plural in zip(self._catalogs, self._plurals):
            if trans.plural.__code__ == plural.__code__: # type: ignore
                cat.update(trans._catalog) # type: ignore
                break
        else:
            self._catalogs.insert(0, trans._catalog.copy()) # type: ignore
            self._plurals.insert(0, trans.plural) # type: ignore

    def get(self, key: str, default: str | None = None) -> str | None:
        missing = object()
        for cat in self._catalogs:
            result = cat.get(key, missing)
            if result is not missing:
                return result # type: ignore
        return default

    def plural(self, msgid: str, num: int):
        for cat, plural in zip(self._catalogs, self._plurals):
            tmsg = cat.get((msgid, plural(num))) # type: ignore
            if tmsg is not None:
                return tmsg
        raise KeyError