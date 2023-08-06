# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable

import jinja2
import jinja2.ext
import jinja2.parser
from jinja2 import nodes


class BaseWrapExtension(jinja2.ext.Extension):
    tags: set[str]
    template: str

    def parse(self, parser: jinja2.parser.Parser):
        tag = parser.stream.current.value
        lineno = next(parser.stream).lineno
        args, kwargs = self.parse_args(parser)
        body = parser.parse_statements(tuple(['name:end{}'.format(tag)]), drop_needle=True)

        return nodes.CallBlock(self.call_method('wrap', args, kwargs), [], [], body).set_lineno(lineno)

    def parse_args(self, parser: jinja2.parser.Parser) -> tuple[list[Any], list[Any]]:
        args: list[Any] = []
        kwargs: list[Any] = []
        require_comma = False

        while parser.stream.current.type != 'block_end':
            if require_comma:
                parser.stream.expect('comma')

            if parser.stream.current.type == 'name' and parser.stream.look().type == 'assign':
                key = parser.stream.current.value
                parser.stream.skip(2)
                value = parser.parse_expression()
                kwargs.append(nodes.Keyword(key, value, lineno=value.lineno))
            else:
                if kwargs:
                    parser.fail('Invalid argument syntax for WrapExtension tag',
                                parser.stream.current.lineno)
                args.append(parser.parse_expression())

            require_comma = True

        return args, kwargs

    @jinja2.pass_context
    def wrap(
        self,
        context: dict[str, Any],
        caller: Callable[..., Any],
        template: str | None = None,
        *args: Any,
        **kwargs: Any
    ) -> str:
        t = self.environment.get_template(template or self.template)
        return t.render(dict(context, content=caller(), **kwargs))