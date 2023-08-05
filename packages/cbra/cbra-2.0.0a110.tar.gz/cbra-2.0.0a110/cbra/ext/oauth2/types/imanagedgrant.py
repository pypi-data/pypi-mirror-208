# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Protocol

from headless.ext import oauth2
from headless.types import IClient

from .iaccesstoken import IAccessToken
from .ifrontendstorage import IFrontendStorage


class IManagedGrant(Protocol):
    __module__: str = 'cbra.ext.oauth2.types'

    def has_access_token(self, resource: str) -> bool: ...
    async def get_resource_client(
        self,
        storage: IFrontendStorage,
        client: oauth2.Client,
        resource: str,
        scope: set[str] | None = None
    ) -> IClient[Any, Any]:
        ...

    async def refresh(
        self,
        storage: IFrontendStorage,
        client: oauth2.Client,
        resource: str | None = None,
        scope: set[str] | None = None
    ) -> IAccessToken:
        ...