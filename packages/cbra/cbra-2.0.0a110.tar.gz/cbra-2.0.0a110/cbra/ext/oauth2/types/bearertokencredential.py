# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from headless.core import BaseCredential
from headless.types import IRequest

from .iaccesstoken import IAccessToken
from .iaccesstokenobtainer import IAccessTokenObtainer


class BearerTokenCredential(BaseCredential):
    __module__: str = 'cbra.ext.oauth2.types'
    access_token: IAccessToken | None
    factory: IAccessTokenObtainer

    def __init__(
        self,
        factory: IAccessTokenObtainer,
        access_token: IAccessToken | None = None,
    ):
        self.access_token = access_token
        self.factory = factory

    async def add_to_request(self, request: IRequest[Any]) -> None:
        if self.access_token is None or self.access_token.is_expired():
            self.access_token = await self.factory.obtain()
        request.add_header('Authorization', f'Bearer {str(self.access_token)}')