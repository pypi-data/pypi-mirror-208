# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import copy
from typing import Any

import jinja2

from cbra.core.conf import settings
from cbra.core import translation


class BaseEmailSender:
    __module__: str = 'cbra.ext.email'

    @property
    def environment(self) -> jinja2.Environment:
        env = jinja2.Environment(
            loader=jinja2.ChoiceLoader([
                jinja2.FileSystemLoader('res/templates/email'),
                jinja2.PackageLoader('cbra.ext.email', 'templates'),
            ]),
            undefined=jinja2.StrictUndefined,
            extensions=[
                'jinja2.ext.i18n',
                'cbra.ext.email.AccessCodeExtension',
                'cbra.ext.email.ButtonExtension',
                'cbra.ext.email.ParagraphExtension',
                'cbra.ext.email.SectionExtension',
            ]
        )
        env.install_gettext_callables( # type: ignore
            gettext=translation.gettext,
            ngettext=translation.ngettext,
            newstyle=True
        )
        return env

    def get_template_context(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Update the given context with some default variables."""
        ctx = copy.deepcopy(ctx)
        ctx.update({
            'settings': settings
        })
        return ctx

    def get_template(self, template_name: str) -> jinja2.Template:
        """Return a :class:`jinja2.Template` instance using the
        configured environment (see :attr:`environment`).
        """
        return self.environment.get_template(template_name)
    
    def render_template(self, template_name: str, ctx: dict[str, Any]) -> str:
        """Render a template specified by `template_name` with the given
        context dictionary.
        """
        t = self.get_template(template_name)
        return t.render(**ctx)
    
    def render_templates(
        self,
        templates: dict[str, str],
        ctx: dict[str, Any]
    ) -> list[tuple[str, str]]:
        """Render the mapping of content types to template names."""
        return [
            (content_type, self.render_template(name, ctx))
            for content_type, name in templates.items()
        ]