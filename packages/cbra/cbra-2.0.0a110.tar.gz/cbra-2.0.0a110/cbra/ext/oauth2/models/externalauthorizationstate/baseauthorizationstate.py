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

import pydantic

from ...types import AuthorizationRequestIdentifier
from ...types import ClientIdentifier


class BaseAuthorizationState(pydantic.BaseModel):
    client_id: ClientIdentifier
    created: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    iss: str
    kind: str
    nonce: str = pydantic.Field(
        default_factory=lambda: secrets.token_hex(48)
    )
    redirect_uri: str
    return_url: str | None = None
    request_id: AuthorizationRequestIdentifier
    state: str = pydantic.Field(
        default_factory=lambda: secrets.token_hex(48)
    )

    def get_prompt_url(self) -> str:
        raise NotImplementedError