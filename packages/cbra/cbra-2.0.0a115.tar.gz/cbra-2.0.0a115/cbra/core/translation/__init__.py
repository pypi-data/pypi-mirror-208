# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .languagecontext import LanguageContext
from .translation import Translation


__all__: list[str] = [
    'LanguageContext',
    'Translation',
]

def gettext(message: str) -> str:
    """Return a string holding the translation of `message` in the currently
    active language, or `message` if no translation was found.
    """
    eol_message = message.replace("\r\n", "\n").replace("\r", "\n")
    if eol_message:
        result = LanguageContext.gettext(eol_message)
    else:
        # Return an empty value of the corresponding type if an empty message
        # is given, instead of metadata, which is the default gettext behavior.
        result = type(message)("")
    return result


def ngettext(singular: str, plural: str, number: int):
    return LanguageContext.ngettext(singular, plural, number)


def override(language: str) -> LanguageContext:
    return LanguageContext(language)