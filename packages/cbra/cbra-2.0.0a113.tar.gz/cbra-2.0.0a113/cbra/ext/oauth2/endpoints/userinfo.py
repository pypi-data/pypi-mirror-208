# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import NoReturn

from headless.ext.oauth2.models import ClaimSet

from ..params import RequestAccessToken
from ..types import BearerTokenException
from ..types import IssuedAccessToken
from .base import AuthorizationServerEndpoint


class UserInfoEndpoint(AuthorizationServerEndpoint):
    principal: RequestAccessToken # type: ignore
    name: str = 'oauth2.userinfo'
    path: str = '/userinfo'
    response_model_exclude_none: bool = True
    require_authentication: bool = False
    summary: str = 'UserInfo Endpoint'

    async def get(self) -> ClaimSet:
        if not self.principal.token_id:
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_token',
                error_description=(
                    "Provide an access token using the `Authorization` header "
                    "to query the UserInfo endpoint."
                )
            )
        token = await self.storage.fetch(self.principal.token_id)
        if token is None or token.is_expired():
            await self.on_token_invalid(token)
            assert False
        return ClaimSet.parse_obj(token.claims)
    
    async def on_token_invalid(
        self,
        token: IssuedAccessToken | None
    ) -> NoReturn:
        if token is not None:
            await self.storage.destroy(token)
        raise BearerTokenException(
            scheme='Bearer',
            error='invalid_token',
            error_description=(
                "The access token provided is expired, revoked, malformed, "
                "or invalid for other reasons."
            )
        )