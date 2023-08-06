# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from datetime import datetime
from datetime import timezone

import pydantic
from canonical import EmailAddress
from headless.ext import oauth2

from cbra.types import VersionedCipherText
from cbra.ext.security import ApplicationKeychain
from ...types import NoRefreshTokenReturned


class ManagedGrant(pydantic.BaseModel):
    """A grant received from an external identity
    provider.
    """
    client_id: str
    email: EmailAddress | None = None
    iss: str
    received: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    refresh_token: str | VersionedCipherText
    scope: set[str] = set()
    sub: str | None = None
    token_endpoint: str
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
            'sub': sub,
            'token_endpoint': client.server.token_endpoint
        })

    async def decrypt(self, keychain: ApplicationKeychain):
        if isinstance(self.refresh_token, VersionedCipherText):
            self.refresh_token = await keychain.decrypt(
                self.refresh_token,
                parser=lambda _, pt: bytes.decode(pt, 'utf-8')
            )

    async def encrypt(self, keychain: ApplicationKeychain):
        if not isinstance(self.refresh_token, VersionedCipherText):
            self.refresh_token = await keychain.encrypt(self.refresh_token)

    async def refresh(self, client: oauth2.Client, resource: str | None = None):
        """Invoke the Token Endpoint to refresh an access token and
        refresh token, and correspondingly update the :attr`:refresh_token`
        attribute.
        """
        assert isinstance(self.refresh_token, str)
        response = await client.refresh_token(
            token=self.refresh_token,
            resource=resource,
            scope=self.scope or None
        )
        if response.refresh_token is None:
            raise NoRefreshTokenReturned(
                "The authorization server did not return a refresh "
                "token."
            )
        self.refresh_token = response.refresh_token
        return response