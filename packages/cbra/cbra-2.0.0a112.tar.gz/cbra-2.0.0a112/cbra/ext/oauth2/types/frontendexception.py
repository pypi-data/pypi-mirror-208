# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse

import fastapi

from cbra.types import Abortable


class FrontendException(Abortable):
    __module__: str = 'cbra.ext.oauth2.types'
    return_url: str
    params: dict[str, str]

    def __init__(self, return_url: str, **params: str) -> None:
        self.params = params

        p: list[str | None] = list([
            str(x) if x else None
            for x in urllib.parse.urlparse(return_url)
        ])
        q: dict[str, str] = dict(urllib.parse.parse_qsl(p[4]))
        q.update(self.params)
        p = list(p)
        p[4] = urllib.parse.urlencode(q) # type: ignore
        self.return_url = urllib.parse.urlunparse(p)

    async def as_response(self) -> fastapi.Response:
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=self.return_url
        )
    