# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
import secrets
from datetime import datetime
from datetime import timezone
from typing import Any

import pydantic
from headless.types import IClient
from headless.ext import oauth2
from ..client import AccessTokenFactory
from ..types import BearerToken
from ..types import BearerTokenCredential
from ..types import ResourceAccessTokenIdentifier
from ..types import ResourceServerAccessToken
from ..types import IFrontendStorage


# TODO: Remove this code

class ManagedGrant(pydantic.BaseModel):
    """A grant received from an external identity
    provider.
    """
    client_id: str
    id: str = pydantic.Field(
        default_factory=lambda: secrets.token_urlsafe(96)
    )
    iss: str
    received: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    refresh_token: str
    scope: set[str] = set()
    sub: str | None = None
    version: int = 0

    @classmethod
    def parse_response(
        cls,
        client: oauth2.Client,
        response: oauth2.TokenResponse,
        sub: str | None = None
    ):
        """Create a new :class:`ManagedGrant` using the response from the
        Token Endpoint.
        """
        return cls.parse_obj({
            'client_id': client.client_id,
            'iss': client.get_issuer(),
            'refresh_token': response.refresh_token,
            'scope': set(filter(bool, re.split('\\s+', response.scope or ''))),
            'sub': sub
        })

    def get_access_token_id(
        self,
        resource: str
    ) -> ResourceAccessTokenIdentifier:
        """Return a :class:`~cbra.ext.oauth2.types.ResourceAccessTokenIdentifier`
        instance identifying an access token from this grant for the specified
        resource.
        """
        return ResourceAccessTokenIdentifier(grant_id=self.id, resource=resource)

    async def refresh(
        self,
        storage: IFrontendStorage,
        client: oauth2.Client,
        resource: str | None = None,
        scope: set[str] | None = None
    ) -> BearerToken:
        """Refreshes the refresh token using the given client."""
        response = await client.refresh_token(
            token=self.refresh_token,
            resource=resource,
            scope=scope
        )
        if response.refresh_token is not None:
            self.refresh_token = response.refresh_token
        if resource is not None:
            assert client.server.metadata is not None
            assert client.server.metadata.issuer is not None
            at = ResourceServerAccessToken.parse_response(
                grant_id=self.id,
                issuer=client.server.metadata.issuer,
                response=response,
                resource=resource,
            )
            await storage.persist(at)
        await storage.persist(self)
        return BearerToken.parse_token_response(response)

    async def get_resource_client(
        self,
        storage: IFrontendStorage,
        client: oauth2.Client,
        resource: str,
        scope: set[str] | None = None
    ) -> IClient[Any, Any]:
        token = await storage.get(self.get_access_token_id(resource))
        if token is None:
            token = await self.refresh(storage, client, resource, scope=scope)
        return oauth2.ResourceServer(
            base_url=resource,
            credential=BearerTokenCredential(
                factory=AccessTokenFactory(
                    storage=storage,
                    client=client,
                    resource=resource,
                    grant=self # type: ignore
                ),
                access_token=token
            )
        )