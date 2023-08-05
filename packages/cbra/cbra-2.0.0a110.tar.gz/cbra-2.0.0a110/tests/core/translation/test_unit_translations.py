# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pathlib

import pytest

from cbra.core.translation import Translation


@pytest.mark.parametrize("language,tmsg", [
    ("nl_NL", "Hallo wereld!"),
    ("nl", "Hallo wereld!"),
    ("en", "Hello world!"),
    ("de", "Hello world!"),
])
def test_gettext(language: str, tmsg: str):
    curdir = pathlib.Path(__file__).parent
    translations = Translation(language, localedirs=[
        "res/locale",
        curdir.joinpath("locale")
    ])
    assert translations.gettext("Hello world!") == tmsg


@pytest.mark.parametrize("language,tmsg", [
    ("nl_NL", "Dit is een vertaalde string!"),
    ("nl", "Dit is een vertaalde string!"),
])
def test_gettext_merged(language: str, tmsg: str):
    curdir = pathlib.Path(__file__).parent
    translations = Translation(language, localedirs=[
        "res/locale",
        curdir.joinpath("locale")
    ])
    assert translations.gettext("This is a translated string!") == tmsg