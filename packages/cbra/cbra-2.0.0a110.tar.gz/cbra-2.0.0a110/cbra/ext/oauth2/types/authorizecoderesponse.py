# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from headless.ext.oauth2 import Client
from headless.ext.oauth2 import TokenResponse
from headless.ext.oauth2.models import AuthorizationCode

from cbra.types import IDependant
from .authorizationstateidentifier import AuthorizationStateIdentifier
from .authorizationstate import AuthorizationState



class AuthorizeCodeResponse(pydantic.BaseModel, IDependant):
    code: str = pydantic.Field(
        default=...
    )

    iss: str | None = pydantic.Field(
        default=None
    )

    state: AuthorizationStateIdentifier = pydantic.Field(
        default=...
    )

    async def obtain(self, client: Client, params: AuthorizationState) -> TokenResponse:
        return await client.exchange_authorization_code(
            dto=AuthorizationCode(code=self.code, state=params.state),
            redirect_uri=str(params.redirect_uri)
        )