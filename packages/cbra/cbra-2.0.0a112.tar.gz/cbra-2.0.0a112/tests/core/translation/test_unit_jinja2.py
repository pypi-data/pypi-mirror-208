# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import jinja2
import pytest

from cbra.core import translation


@pytest.mark.parametrize("language,tmsg", [
    ('nl-NL', "Dit is een vertaalde string!"),
    ('nl', "Dit is een vertaalde string!"),
    ('xx', "This is a translated string!")
])
def test_gettext(language: str, tmsg: str):
    env = jinja2.Environment(
        extensions=['jinja2.ext.i18n']
    )
    env.install_gettext_callables( # type: ignore
        gettext=translation.gettext,
        ngettext=translation.ngettext,
        newstyle=True
    )
    t = env.from_string("{{ gettext('This is a translated string!') }}")
    with translation.override(language):
        assert t.render() == tmsg

    assert t.render() == 'This is a translated string!'