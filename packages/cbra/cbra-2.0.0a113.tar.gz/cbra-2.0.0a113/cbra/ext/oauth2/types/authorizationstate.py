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
from datetime import timezone
from typing import TypeVar

import pydantic
from cbra.types import PersistedModel
from headless.ext.oauth2 import Client
from headless.ext.oauth2.types import ResponseMode
from headless.ext.oauth2.types import ResponseType


T = TypeVar('T', bound='AuthorizationState')


class AuthorizationState(PersistedModel):
    client_id: str = pydantic.Field(
        default=...
    )

    created: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    nonce: str = pydantic.Field(
        default=...
    )

    redirect_uri: str = pydantic.Field(
        default=...
    )

    return_uri: str = pydantic.Field(
        default='/'
    )

    response_mode: ResponseMode = pydantic.Field(
        default=...
    )

    response_type: ResponseType = pydantic.Field(
        default=...
    )

    state: str = pydantic.Field(
        default=...,
        primary_key=True
    )

    scope: set[str] = pydantic.Field(
        default_factory=set
    )

    @classmethod
    def new(
        cls: type[T],
        *,
        client_id: str,
        redirect_uri: str,
        response_mode: ResponseMode,
        response_type: ResponseType,
        return_uri: str = '/'
    ) -> T:
        return cls(
            client_id=client_id,
            nonce=secrets.token_urlsafe(48),
            redirect_uri=redirect_uri,
            return_uri=return_uri,
            response_mode=response_mode,
            response_type=response_type,
            state=secrets.token_urlsafe(48),
        )
    
    def is_valid(
        self,
        state: str
    ) -> bool:
        """Return a boolean indicating if the authorization server returned
        a valid response.
        """
        return all([
            self.state == state
        ])
    
    def is_openid(self) -> bool:
        return 'openid' in self.scope

    async def get_authorize_uri(self, client: Client) -> str:
        params: dict[str, str] = {}
        if self.is_openid():
            params['nonce'] = self.nonce
        return await client.authorize(
            state=self.state,
            redirect_uri=self.redirect_uri
        )