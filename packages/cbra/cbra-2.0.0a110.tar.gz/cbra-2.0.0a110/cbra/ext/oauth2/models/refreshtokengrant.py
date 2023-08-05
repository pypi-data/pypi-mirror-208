# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Literal

from headless.ext.oauth2.models import TokenResponse
from headless.ext.oauth2.types import GrantType

from ..types import IAuthorizationServerStorage
from ..types import ITokenBuilder
from ..types import ITokenSigner
from ..types import InvalidGrant
from ..types import InvalidTarget
from ..types import RefreshTokenIdentifier
from ..types import RequestedScope
from .basetokenrequest import BaseTokenRequest
from .resourceowner import ResourceOwner


logger: logging.Logger = logging.getLogger('cbra.endpoint')


class RefreshTokenGrant(BaseTokenRequest):
    grant_type: Literal[GrantType.refresh_token]
    owner: ResourceOwner | None
    refresh_token: RefreshTokenIdentifier
    resource: str | None
    scope: set[str] = set()

    async def create_response(
        self,
        storage: IAuthorizationServerStorage,
        builder: ITokenBuilder,
        signer: ITokenSigner
    ) -> TokenResponse:
        grant = await storage.fetch(self.refresh_token)
        if grant is None or not grant.is_active():
            raise InvalidGrant("The refresh token is not valid.")
        if not grant.allows_scope(self.scope):
            raise InvalidGrant("The scope requested exceeds the granted scope.")
        if self.resource and not grant.allows_resource(self.resource):
            raise InvalidTarget(
                "The requested audience is not allowed with this refresh token."
            )
        refreshed = grant.refresh()
        assert refreshed.token != grant.token
        await storage.destroy(grant)
        await storage.persist(refreshed)

        at, expires_in = builder.rfc9068(
            sub=grant.ppid,
            scope=[RequestedScope.parse_obj({'name': s}) for s in set(self.scope or grant.scope)],
            auth_time=grant.auth_time,
            audience=self.resource
        )
        access_token = await at.sign(signer)
        await self.register_issued_access_token(
            token=at,
            signed=access_token,
            scope=list(self.scope or grant.scope),
            storage=storage,
            sub=grant.sub,
            claims=grant.claims
        )
        return TokenResponse(
            access_token=access_token, # type: ignore
            expires_in=expires_in,
            refresh_token=str(refreshed.token),
            token_type='Bearer'
        )