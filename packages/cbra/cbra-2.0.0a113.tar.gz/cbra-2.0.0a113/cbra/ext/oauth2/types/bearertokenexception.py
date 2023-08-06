# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from cbra.types import Abortable


class BearerTokenException(Abortable):
    error: str
    error_description: str
    scheme: str
    scope: set[str]
    status_code: int = 401

    def __init__(
        self,
        scheme: str,
        error:str,
        error_description: str,
        scope: set[str] | None = None,
        status_code: int = 401
    ) -> None:
        self.error = error
        self.error_description = error_description
        self.scheme = scheme
        self.scope = scope or set()
        self.status_code = status_code

    async def as_response(self) -> fastapi.Response:
        response = fastapi.Response(status_code=self.status_code)
        value = self.scheme
        params: list[str] = []
        if self.error:
            params.append(f'error="{self.error}"')
        if self.error_description:
            params.append(f'error_description="{self.error_description}"')
        if self.scope:
            params.append(f'scope="{str.join(" ", sorted(self.scope))}"')
        if params:
            value += f" {str.join(',', params)}"
        response.headers['WWW-Authenticate'] = value
        return response
