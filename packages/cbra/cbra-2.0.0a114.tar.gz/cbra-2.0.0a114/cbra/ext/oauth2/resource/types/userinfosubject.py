# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from headless.ext.oauth2.models import ClaimSet

from cbra.types import ISubject


class UserInfoSubject(ISubject):
    """Describes a :term:`Resource Owner` of which the claims were
    received from the OpenID Connect UserInfo endpoint.
    """
    __module__: str = 'cbra.ext.oauth2.resource.types'
    claims: ClaimSet

    @property
    def sub(self) -> str:
        return self.claims.sub

    def __init__(self, claims: dict[str, Any] | ClaimSet):
        if isinstance(claims, dict):
            claims = ClaimSet.parse_obj(claims)
        self.claims = claims
        self.email = claims.email

    def is_authenticated(self) -> bool:
        return True

    def get_display_name(self) -> str:
        raise NotImplementedError