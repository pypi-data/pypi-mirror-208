# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext import oauth2

from ..types import IAccessToken
from ..types import IAccessTokenObtainer
from ..types import IFrontendStorage
from ..types import IManagedGrant


class AccessTokenFactory(IAccessTokenObtainer):
    __module__: str = 'cbra.ext.oauth2.client'
    client: oauth2.Client
    grant: IManagedGrant
    resource: str
    storage: IFrontendStorage

    def __init__(
        self,
        storage: IFrontendStorage,
        client: oauth2.Client,
        grant: IManagedGrant,
        resource: str
    ):
        self.client = client
        self.grant = grant
        self.resource = resource
        self.storage = storage

    async def obtain(self, scope: set[str] | None = None) -> IAccessToken:
        return await self.grant.refresh(
            storage=self.storage,
            client=self.client,
            resource=self.resource,
            scope=scope
        )