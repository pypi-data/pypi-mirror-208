# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# type: ignore
import gettext
import pathlib
from typing import Callable

from .translationcatalog import TranslationCatalog
from .types import ITranslation
from .utils import to_language
from .utils import to_locale


CBRA_DOMAIN: str = "cbra"


class Translation(gettext.GNUTranslations, ITranslation):
    """Set up the GNUTranslations context with regard to output charset.

    This translation object will be constructed out of multiple GNUTranslations
    objects by merging their catalogs. It will construct an object for the
    requested language and add a fallback to the default language, if it's
    different from the requested language.
    """
    __module__: str = 'cbra.core.translation'
    default_domain: str = CBRA_DOMAIN
    domain: str
    plural: Callable[[int], int]
    _catalog: TranslationCatalog | None
    __language: str
    __locale: str
    __localedirs: list[str]

    def __init__(
        self,
        language: str,
        domain: str | None = None,
        localedirs: list[str | pathlib.Path] | None = None
    ) -> None:
        super().__init__()
        self.domain = domain or self.default_domain
        self._catalog = None
        self.__language = to_language(language)
        self.__locale = to_locale(language)
        self.__localedirs = [str(x) for x in (localedirs or [])]

        # If a language doesn't have a catalog, use the Germanic default for
        # pluralization: anything except one is pluralized.
        self.plural = lambda n: int(n != 1)

        self._init_catalog()
        for dirname in self.__localedirs:
            self.merge(self.create_gnu_translation(dirname))

        if self._catalog is None:
            self._catalog = TranslationCatalog()

    def _init_catalog(self):
        """Create a base catalog using global translations."""
        self.merge(self.create_gnu_translation(pathlib.Path(__file__).parent.joinpath("locale")))

    def create_gnu_translation(
        self,
        dirname: str,
        use_null_fallback: bool = True
    ) -> gettext.GNUTranslations | gettext.NullTranslations:
        """Return a mergeable :class:`gettext.GNUTranslations` instance.
        A convenience wrapper. By default gettext uses ``fallback=False``.
        Using param `use_null_fallback` to avoid confusion with any other
        references to `fallback`.
        """
        return gettext.translation(
            domain=self.domain,
            localedir=dirname,
            languages=[self.__locale],
            fallback=use_null_fallback
        )

    def merge(self, other: gettext.GNUTranslations | gettext.NullTranslations):
        """Merge another translation into this catalog."""
        if not getattr(other, "_catalog", None):
            assert isinstance(other, gettext.NullTranslations)
            return  # NullTranslations() has no _catalog
        if self._catalog is None:
            # Take plural and _info from first catalog found.
            self.plural = other.plural
            self._info = other._info.copy()
            self._catalog = TranslationCatalog(other)
        else:
            self._catalog.update(other)
        if other._fallback:
            self.add_fallback(other._fallback)