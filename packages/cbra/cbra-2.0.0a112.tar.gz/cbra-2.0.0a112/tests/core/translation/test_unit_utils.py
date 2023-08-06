# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from cbra.core.translation import utils


@pytest.mark.parametrize("language,result", [
    ("en_US", "en-us"),
    ("en", "en"),
])
def test_locale_to_language(language: str,  result: str):
    assert utils.to_language(language) == result


@pytest.mark.parametrize("language,result", [
    ("en-us", "en_US"),
    ("sr-latn", "sr_Latn"),
    ("en", "en"),
])
def test_language_to_locale(language: str,  result: str):
    assert utils.to_locale(language) == result
