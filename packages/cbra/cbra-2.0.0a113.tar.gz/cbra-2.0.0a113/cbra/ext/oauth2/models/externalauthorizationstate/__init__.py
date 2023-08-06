# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse
from typing import Any
from typing import Union

import pydantic
from headless.ext.oauth2.models import TokenResponse

from ...types import AuthorizationRequestIdentifier
from ...types import ClientIdentifier
from ...types import FatalAuthorizationException
from ...types import OIDCProvider
from .downstreamauthorizationstate import DownstreamAuthorizationState
from .loginauthorizationstate import LoginAuthorizationState
from .recoveryauthorizationstate import RecoveryAuthorizationState


class ExternalAuthorizationState(pydantic.BaseModel):
    __root__: Union[
        DownstreamAuthorizationState,
        LoginAuthorizationState,
        RecoveryAuthorizationState
    ]

    @property
    def id(self) -> str:
        return self.__root__.state

    @property
    def client_id(self) -> ClientIdentifier:
        return self.__root__.client_id

    @property
    def kind(self) -> str:
        return self.__root__.kind

    @property
    def request_id(self) -> AuthorizationRequestIdentifier:
        return self.__root__.request_id

    @property
    def return_url(self) -> str | None:
        return self.__root__.return_url

    @classmethod
    def new(
        cls,
        provider: OIDCProvider,
        client_id: str,
        kind: str,
        request_id: str,
        redirect_uri: str,
        **kwargs: Any
    ):
        return cls.parse_obj({
            **kwargs,
            'client_id': client_id,
            'iss': provider.client.metadata.issuer,
            'kind': kind,
            'redirect_uri': redirect_uri,
            'request_id': request_id,
        })

    def set_return_url(self, url: str, **params: str) -> None:
        p: list[str] = list(urllib.parse.urlparse(url)) # type: ignore
        p[4] = urllib.parse.urlencode(
            {**params, **dict(urllib.parse.parse_qsl(p[4]))},
            quote_via=urllib.parse.quote
        )
        self.__root__.return_url = urllib.parse.urlunparse(p)

    async def get_redirect_uri(
        self,
        provider: OIDCProvider,
        callback_uri: str
    ) -> str:
        return await provider.get_redirect_uri(
            redirect_uri=callback_uri,
            state=self.__root__.state,
            nonce=self.__root__.nonce
        )
    
    async def obtain(
        self,
        provider: OIDCProvider,
        code: str,
        url: str,
        iss: str | None = None
    ) -> TokenResponse:
        if provider.client.metadata.authorization_response_iss_parameter_supported\
        and iss != self.__root__.iss:
            raise FatalAuthorizationException("Authorization response from untrusted issuer.")
        token = await provider.obtain(
            code=code,
            state=self.__root__.state,
            redirect_uri=url
        )
        _, oidc = await provider.verify(token, nonce=self.__root__.nonce)
        if oidc is None:
            raise FatalAuthorizationException(
                "The OIDC ID Token returned by the authorization server "
                "was malformed, invalid or otherwise unusable."
            )
        if oidc.email is None:
            raise FatalAuthorizationException(
                "The authorization server did not provide the 'email' "
                "claim."
            )
        return token