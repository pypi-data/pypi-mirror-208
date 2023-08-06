# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from cbra.types import RequestLanguage


def test_multiple_weighted():
    l = RequestLanguage("nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6")
    assert l.languages[0].code == 'nl-NL'
    assert l.languages[1].code == 'nl'
    assert l.languages[2].code == 'en-US'
    assert l.languages[3].code == 'en'
    assert l.languages[4].code == 'es'


@pytest.mark.parametrize("language", [
    "nl-nl",
    "nl",
    "en-us",
    "en",
    "es"
])
def test_selectable(language: str):
    l = RequestLanguage("nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6")
    assert str.lower(l.select({language})) == str.lower(language)


def test_no_header_provided_returns_default_has_en_default():
    l = RequestLanguage()
    assert l.select({'foo', 'bar', 'baz'}) == 'en'


def test_none_provided_returns_default_has_en_default():
    l = RequestLanguage(None)
    assert l.select({'foo', 'bar', 'baz'}) == 'en'


def test_none_provided_returns_default():
    l = RequestLanguage(None)
    assert l.select({'foo', 'bar', 'baz'}, 'nl') == 'nl'