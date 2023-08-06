# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi
from headless.ext.oauth2 import Error
from headless.types import IClient

from .params import RequestedResourceServerClient
from .tokenhandlerendpoint import TokenHandlerEndpoint


class FrontendProxyEndpoint(TokenHandlerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    name: str = 'bff.proxy'
    path: str = '/oauth/v2/resources/{resource}{path:path}'
    resource: IClient[Any, Any] = RequestedResourceServerClient
    resource_path: str = fastapi.Path(default=..., alias='path')
    summary: str = 'Frontend Proxy Endpoint'

    async def head(self) -> fastapi.Response:
        return await self.handle('HEAD')

    async def get(self) -> fastapi.Response:
        return await self.handle('GET')

    async def post(self) -> fastapi.Response:
        return await self.handle('POST')

    async def put(self) -> fastapi.Response:
        return await self.handle('PUT')

    async def patch(self) -> fastapi.Response:
        return await self.handle('PATCH')

    async def delete(self) -> fastapi.Response:
        return await self.handle('DELETE')
    
    async def handle(self, method: str) -> fastapi.Response:
        # Discard all other headers except the Content-Type header
        content: bytes | None = None
        headers: dict[str, str | None] = {}
        if method in {'POST', 'PUT', 'PATCH'}:
            headers['Content-Type'] = self.request.headers.get('Content-Type')
            content = await self.request.body()
        try:
            response = await self.resource.request(
                content=content,
                headers={k: v for k, v in headers.items() if v},
                method=method,
                url=self.resource_path,
            )
        except Error as exception:
            return await self.on_authorization_error(exception)
        return fastapi.Response(
            content=response.content,
            headers=dict(response.headers),
            status_code=response.status_code
        )

    async def on_authorization_error(self, error: Error) -> fastapi.Response:
        # Failure during interaction with the resource server. We have no way to
        # resolve this, so instruct the client to obtain a new grant.
        return fastapi.Response(
            status_code=401,
            headers={'WWW-Authenticate': 'Bearer error="invalid_token"'}
        )