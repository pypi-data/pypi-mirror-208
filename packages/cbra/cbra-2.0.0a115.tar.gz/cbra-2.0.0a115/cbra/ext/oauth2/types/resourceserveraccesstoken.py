# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pydantic
from headless.ext import oauth2


class ResourceServerAccessToken(pydantic.BaseModel):
    """Maintains a single access token for a specific :term:`Resource Server`.
    This storage model may be used to implement shadow tokens, usually in
    for a backend-for-frontend combined with a browser-based application (SPA).
    """
    access_token: str = pydantic.Field(
        default=...
    )

    expires: datetime = pydantic.Field(
        default=...
    )

    grant_id: str = pydantic.Field(
        default=...
    )

    issuer: str = pydantic.Field(
        default=...
    )

    resource: str = pydantic.Field(
        default=...
    )

    @classmethod
    def parse_response(cls, grant_id: str, issuer: str, resource: str, response: oauth2.TokenResponse):
        now = datetime.now(timezone.utc)
        return cls.parse_obj({
            'access_token': str(response.access_token),
            'expires': now + timedelta(seconds=response.expires_in),
            'grant_id': grant_id,
            'issuer': issuer,
            'resource': resource,
        })

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.expires <= now

    async def refresh(self, client: oauth2.Client) -> None:
        """Refreshes the access token using the given client."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.access_token