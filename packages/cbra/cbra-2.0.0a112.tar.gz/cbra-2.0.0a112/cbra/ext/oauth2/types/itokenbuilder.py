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

from headless.ext.oauth2.types import GrantType

from cbra.core.iam.models import Subject
from .iauthorizationrequest import IAuthorizationRequest
from .iresourceowner import IResourceOwner
from .refreshtokenpolicytype import RefreshTokenPolicyType
from .rfc9068accesstoken import RFC9068AccessToken
from .requestedscope import RequestedScope
from .signableoidctoken import SignableOIDCToken


class ITokenBuilder(Protocol):
    __module__: str = 'cbra.ext.oauth2.types'

    def rfc9068(
        self,
        sub: int | str,
        scope: list[RequestedScope],
        auth_time: int,
        audience: str | None = None,
    ) -> tuple[RFC9068AccessToken, int]:
        ...

    async def refresh_token(
        self,
        grant_type: GrantType,
        client_id: str,
        sector_identifier: str,
        sub: int,
        ppid: int,
        claims: dict[str, Any],
        scope: list[RequestedScope],
        renew: RefreshTokenPolicyType,
        ttl: int,
        auth_time: int,
        resources: list[str] | None = None
    ) -> str:
        ...

    def id_token(
        self,
        subject: Subject,
        ppid: int,
        nonce: str,
        scope: list[RequestedScope],
        access_token: str | None,
        auth_time: int | None = None,
        authorization_code: str | None = None,
        request: IAuthorizationRequest | None = None,
        owner: IResourceOwner | None = None,
    ) -> SignableOIDCToken:
        ...

    async def userinfo(
        self,
        subject: Subject,
        owner: IResourceOwner,
        request: IAuthorizationRequest,
        scope: list[RequestedScope],
    ) -> dict[str, Any]:
        ...