# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import TypeVar

import pydantic
from headless.ext.oauth2.types import GrantType

from ..types import RefreshTokenPolicyType
from ..types import RefreshTokenType


T = TypeVar('T', bound='RefreshToken')


class RefreshToken(pydantic.BaseModel):
    auth_time: int
    created: datetime
    claims: dict[str, Any] = {}
    client_id: str
    granted: datetime
    grant_id: int = 0
    grant_type: GrantType
    expires: datetime
    ppid: int
    renew: RefreshTokenPolicyType
    resources: list[str] = []
    scope: set[str]
    sector_identifier: str
    sub: int
    ttl: int
    token: RefreshTokenType

    @pydantic.root_validator(pre=True) # type: ignore
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        expires = values.get('expires')
        created = values.setdefault('created', datetime.now(timezone.utc))
        ttl = values.get('ttl')
        values.setdefault('granted', created)
        if ttl is not None and not expires:
            assert isinstance(ttl, int)
            values['expires'] = created + timedelta(seconds=ttl)
        if not values.get('token'):
            values['token'] = RefreshTokenType(secrets.token_urlsafe(48))
        return values

    def allows_resource(self, resource: str) -> bool:
        """Return a boolean if the refresh token allows the given resource."""
        return resource in self.resources

    def allows_scope(self, requested: set[str]) -> bool:
        """Return a boolean indicating if the :term:`Refresh Token` allows
        issuing an :term:`Access Token` with the given scope.
        """
        return requested <= self.scope

    def refresh(self: T) -> T:
        """Refresh the token."""
        now = datetime.now(timezone.utc)
        grant = type(self).parse_obj({
            **self.dict(),
            'created': datetime.now(timezone.utc),
            'token': RefreshTokenType(secrets.token_urlsafe(48))
        })
        if grant.renew == RefreshTokenPolicyType.rolling:
            grant.expires = now + timedelta(seconds=self.ttl)
        if grant.renew == RefreshTokenPolicyType.static:
            grant.expires = self.expires
        return grant

    def can_use(self, scope: set[str]) -> bool:
        return self.allows_scope(scope)

    def is_active(self) -> bool:
        return datetime.now(timezone.utc) < self.expires