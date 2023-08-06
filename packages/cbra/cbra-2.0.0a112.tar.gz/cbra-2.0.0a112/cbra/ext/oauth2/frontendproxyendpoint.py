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
        response = await self.resource.request(method=method, url=self.resource_path)
        return fastapi.Response(
            content=response.content,
            headers=dict(response.headers),
            status_code=response.status_code
        )