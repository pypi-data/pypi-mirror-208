# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Awaitable
from typing import Callable
from typing import TypeVar

import fastapi
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from headless.ext import oauth2
from headless.ext.oauth2.models import ClaimSet
from cbra.types import IDependant
from cbra.types import IPrincipal
from cbra.types import ISubject
from cbra.types import Request
from cbra.types import ServiceNotAvailable
from ..types import BearerTokenException
from ..types import IssuedAccessTokenIdentifier
from ..types import RFC9068AccessToken


P = TypeVar('P', bound='RequestAccessToken')
logger: logging.Logger = logging.getLogger('cbra.endpoint')


class RequestAccessToken(IDependant, IPrincipal):
    __module__: str = 'cbra.ext.oauth2.params'
    authorization: HTTPAuthorizationCredentials | None
    supported_schemes: set[str] = {"bearer"}
    token: RFC9068AccessToken | None = None

    @property
    def token_id(self) -> IssuedAccessTokenIdentifier | None:
        if self.authorization is not None:
            return IssuedAccessTokenIdentifier.parse_token(self.authorization.credentials)

    @property
    def client_id(self) -> str:
        assert self.token is not None
        return self.token.client_id

    def __init__(
        self,
        header: str | None = fastapi.Header(
            default=None,
            alias='Authorization',
            title="Authorization",
            description="An RFC 9068 access token."
        )
    ):
        self.authorization = None
        scheme, credentials = get_authorization_scheme_param(header)
        if not scheme and credentials:
            raise BearerTokenException(
                'Bearer', 'invalid_token', "Malformed Authorization header."
            )
        if scheme:
            if str.lower(scheme) not in self.supported_schemes:
                raise BearerTokenException('Bearer', 'invalid_token', 'Unsupported scheme')
            if not credentials:
                raise BearerTokenException('Bearer', 'invalid_token', 'Missing token')
            self.authorization = HTTPAuthorizationCredentials(
                scheme=scheme,
                credentials=credentials
            )
            self.token = RFC9068AccessToken.parse_jwt(self.authorization.credentials)

    def is_anonymous(self) -> bool:
        return self.authorization is None
    
    def get_client(self) -> oauth2.Client:
        assert self.token is not None
        return oauth2.Client(issuer=self.token.iss)

    def get_scope(self) -> set[str]:
        assert self.token is not None
        return self.token.get_scope()

    def has_audience(self) -> bool:
        return False

    async def resolve(
        self,
        resolve: Callable[..., Awaitable[ISubject]]
    ) -> ISubject:
        if self.token is None:
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_request',
                error_description=(
                    "The request did not provide an RFC 9068 access token "
                    "or other credential that is understood by the server."
                ),
                status_code=400
            )
        return await resolve(self)

    async def userinfo(self) -> ClaimSet:
        assert self.authorization is not None
        assert self.token is not None
        async with self.get_client() as client:
            if not client.server.userinfo_endpoint:
                raise BearerTokenException(
                    scheme='Bearer',
                    error='invalid_token',
                    error_description=(
                        "The authorization server that issued the token does not expose "
                        "the OpenID Connect UserInfo endpoint."
                    )
                )
            try:
                return await client.userinfo(self.authorization.credentials)
            except Exception as exc:
                logger.critical(
                    "Caught fatal %s while requesting userinfo from %s",
                    type(exc).__name__, self.token.iss
                )
                raise ServiceNotAvailable

    async def verify(
        self,
        request: Request,
        trusted_issuers: set[str],
        scope: set[str] | None = None
    ):
        """Verifies that the token is accepted by the resource
        server. Raise :exc:`~cbra.ext.oauth2.types.BearerTokenException`
        if the token does not verify.
        """
        assert self.authorization is not None
        assert self.token is not None

        # Ensure that the audience, issuer and scope are accepted by the
        # resource server.
        self.token.verify(
            audiences={
                f'{request.url.scheme}://{request.url.netloc}',
                str(request.url)
            },
            issuers=trusted_issuers,
            scope=scope
        )

        # Verify the signature if all other aspects of the token are verified,
        # to prevent unnecessary remote calls.
        async with self.get_client() as client:
            if not await client.verify_signature(self.authorization.credentials):
                raise BearerTokenException(
                    scheme='Bearer',
                    error='invalid_token',
                    error_description=(
                        "The signature of the access token could not be verified "
                        "using the known keys of the authorization server specified "
                        "in the 'iss' claim."
                    )
                )