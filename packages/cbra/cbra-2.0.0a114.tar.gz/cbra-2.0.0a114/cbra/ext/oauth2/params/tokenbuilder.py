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
from typing import Any

from headless.ext.oauth2.types import GrantType

import cbra.core as cbra
from cbra.core.iam.models import Subject
from cbra.types import IDependant
from ..authorizationserverstorage import AuthorizationServerStorage
from ..models import Client
from ..models import RefreshToken
from ..types import IAuthorizationRequest
from ..types import IResourceOwner
from ..types import RefreshTokenPolicyType
from ..types import RequestedScope
from ..types import RFC9068AccessToken
from ..types import SignableOIDCToken
from .currentissuer import CurrentIssuer
from .requestingclient import RequestingClient


class TokenBuilder(IDependant):
    __module__: str = 'cbra.ext.oauth2.params'
    access_token_ttl: int = 3600
    id_token_ttl: int = 600
    client: Client
    issuer: str
    now: int
    storage: AuthorizationServerStorage

    def __init__(
        self,
        storage: AuthorizationServerStorage = cbra.instance('_AuthorizationServerStorage'),
        issuer: str = CurrentIssuer,
        client: Client = RequestingClient
    ) -> None:
        self.client = client
        self.issuer = issuer
        self.now = int(datetime.now(timezone.utc).timestamp())
        self.storage = storage

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
        claims: dict[str, Any] = {
            'aud': self.client.client_id,
            'auth_time': auth_time,
            'exp': self.now + self.id_token_ttl,
            'azp': self.client.client_id,
            'iat': self.now,
            'iss': self.issuer,
            'nonce': nonce,
            'sub': '0'
        }
        for claim in scope:
            claim.apply(
                subject=subject,
                claims=claims,
                owner=owner, # type: ignore
                request=request,
            )
        return SignableOIDCToken.parse_obj({
            'access_token': access_token,
            'authorization_code': authorization_code,
            'claims': claims
        })

    def rfc9068(
        self,
        sub: int | str,
        scope: list[RequestedScope],
        auth_time: int,
        audience: str | None = None,
    ) -> tuple[RFC9068AccessToken, int]:
        ttl = self.client.access_token_ttl or self.access_token_ttl
        token = RFC9068AccessToken.new(
            client_id=self.client.client_id,
            iss=self.issuer,
            aud=audience or self.issuer,
            sub=str(sub),
            scope=scope,
            auth_time=auth_time,
            now=self.now,
            ttl=ttl
        )
        return token, ttl

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
        instance = RefreshToken.parse_obj({
            'grant_type': grant_type,
            'auth_time': auth_time,
            'claims': claims,
            'client_id': client_id,
            'sector_identifier': sector_identifier,
            'sub': sub,
            'ppid': ppid,
            'scope': list(sorted([x.name for x in scope])),
            'renew': renew,
            'resources': resources or [],
            'ttl': ttl
        })
        await self.storage.persist(instance)
        return instance.token

    async def userinfo(
        self,
        subject: Subject,
        owner: IResourceOwner,
        request: IAuthorizationRequest,
        scope: list[RequestedScope],
    ) -> dict[str, Any]:
        claims: dict[str, Any] = {
            'auth_time': request.auth_time,
            'sub': owner.ppid.value,
            'sct': owner.ppid.sector
        }
        for claim in scope:
            claim.apply(
                subject=subject,
                claims=claims,
                owner=owner, # type: ignore
                request=request,
            )
        return claims