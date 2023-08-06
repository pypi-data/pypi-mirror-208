# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from datetime import timezone
import logging
from typing import Literal

from headless.ext.oauth2.models import TokenResponse
from headless.ext.oauth2.types import GrantType

from ..models import Client
from ..types import IAuthorizationServerStorage
from ..types import ITokenBuilder
from ..types import ITokenSigner
from ..types import InvalidScope
from ..types import InvalidTarget
from ..types import RequestedScope
from .basetokenrequest import BaseTokenRequest


logger: logging.Logger = logging.getLogger('cbra.endpoint')


class ClientCredentialsGrant(BaseTokenRequest):
    client: Client
    grant_type: Literal[GrantType.client_credentials]
    scope: set[str] = set()
    resource: str

    async def create_response(
        self,
        storage: IAuthorizationServerStorage,
        builder: ITokenBuilder,
        signer: ITokenSigner
    ) -> TokenResponse:
        if not self.client.can_use(list(self.scope)):
            raise InvalidScope
        if not self.client.allows_resources({self.resource}):
            raise InvalidTarget
        at, expires_in = builder.rfc9068(
            sub=self.client.client_id,
            scope=[RequestedScope.parse_obj({'name': x}) for x in self.scope],
            auth_time=int(datetime.now(timezone.utc).timestamp()),
            audience=self.resource
        )
        access_token = await at.sign(signer)
        await self.register_issued_access_token(
            token=at,
            signed=access_token,
            scope=list(self.scope),
            storage=storage,
            sub=self.client.client_id,
            claims={
                'sub': self.client.client_id
            }
        )
        return TokenResponse(
            access_token=access_token, # type: ignore
            expires_in=expires_in,
            token_type='Bearer',
            scope=str.join(' ', sorted(self.scope))
        )