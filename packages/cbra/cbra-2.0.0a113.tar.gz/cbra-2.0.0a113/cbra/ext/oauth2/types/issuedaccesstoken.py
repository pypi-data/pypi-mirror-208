# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import hashlib
from typing import Any
from typing import TypeVar

import pydantic

from .rfc9068accesstoken import RFC9068AccessToken


T = TypeVar('T', bound='IssuedAccessToken')


class IssuedAccessToken(pydantic.BaseModel):
    claims: dict[str, Any] = {}
    client_id: str
    encrypted: bool = False
    expires: datetime.datetime
    issuer: str
    scope: list[str]
    sub: int | str
    token_hash: str

    @classmethod
    def parse_rfc9068(
        cls: type[T],
        at: RFC9068AccessToken,
        claims: dict[str, Any],
        signed_token: str,
        scope: list[str],
        sub: int | str
    ) -> T:
        return cls.parse_obj({
            'claims': claims,
            'client_id': at.client_id,
            'expires': at.get_expire_date(),
            'issuer': at.iss,
            'scope': scope,
            'sub': sub,
            'token_hash': hashlib.md5(str.encode(signed_token, 'utf-8')).hexdigest()
        })
    
    def is_expired(self, now: datetime.datetime | None = None) -> bool:
        now = now or datetime.datetime.now(datetime.timezone.utc)
        return self.expires < now