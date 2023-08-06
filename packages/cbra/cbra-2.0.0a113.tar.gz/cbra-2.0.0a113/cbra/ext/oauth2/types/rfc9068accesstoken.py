# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
import secrets
from datetime import datetime
from datetime import timezone

from ckms.jose import Decoder
from ckms.types import Malformed

from .bearertokenexception import BearerTokenException
from .itokensigner import ITokenSigner
from .requestedscope import RequestedScope
from .signable import Signable


class RFC9068AccessToken(Signable):
    iss: str
    aud: str| list[str]
    exp: int
    sub: str
    client_id: str
    iat: int
    jti: str
    auth_time: int | None = None
    acr: str = '0'
    amr: list[str] | None = []
    scope: str | None = None

    @classmethod
    def new(
        cls,
        client_id: str,
        iss: str,
        aud: str | set[str] | list[str],
        sub: str,
        now: int,
        ttl: int,
        scope: list[RequestedScope] | None = None,
        auth_time: int | None = None,
        acr: str = '0',
        amr: list[str] | None = None
    ) -> 'RFC9068AccessToken':
        if isinstance(aud, (list, set)):
            aud = list(sorted(aud))
        
        params: dict[str, int | str | list[str] | None] = {
            'acr': acr,
            'aud': aud,
            'client_id': client_id,
            'exp': now + ttl,
            'iat': now,
            'iss': iss,
            'jti': secrets.token_urlsafe(48),
            'nbf': now,
            'sub': sub,
            'auth_time': auth_time
        }
        if scope is not None:
            params['scope'] = ' '.join(sorted([x.name for x in scope]))
        if amr is not None:
            params['amr'] = amr
        return cls.parse_obj(params)

    @classmethod
    def parse_jwt(cls, token: str) -> 'RFC9068AccessToken':
        typ = None
        try:
            jose, jwt = Decoder.introspect(token)
            if jwt is None:
                raise Malformed
            for header in jose.headers:
                if header.typ is None:
                    continue
                typ = str.lower(header.typ)
                break
            else:
                typ = None
            if typ is None or typ != "at+jwt":
                raise Malformed
        except Malformed:
            raise
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_token',
                error_description=(
                    "The access token provided is expired, revoked, malformed, "
                    "or invalid for other reasons."
                )
            )
        return cls.parse_obj(jwt.dict())

    def get_expire_date(self) -> datetime:
        """Return an aware :class:`datetime.datetime` instance
        representing the date and time that the access token
        expires.
        """
        return datetime.fromtimestamp(float(self.exp), timezone.utc)

    def get_scope(self) -> set[str]:
        return set(filter(bool, re.split(r'\s+', self.scope or '')))

    def is_expired(self) -> bool:
        return self.get_expire_date() < datetime.now(timezone.utc)

    def verify_audience(self, allow: set[str]):
        audience = set([self.aud] if isinstance(self.aud, str) else self.aud)
        if not (audience & allow):
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_token',
                error_description=(
                    "The audience is not accepted by the resource server."
                )
            )

    def verify_scope(self, require: set[str]):
        scope = set(filter(bool, re.split(r'\s+', self.scope or '')))
        if scope < require:
            raise BearerTokenException(
                scheme='Bearer',
                error='insufficient_scope',
                error_description=(
                    "The access token was not granted the required scope for this "
                    "resource."
                ),
                status_code=403
            )

    def verify_expired(self):
        if self.is_expired():
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_token',
                error_description="The access token is expired."
            )

    def verify_issuers(self, allow: set[str]):
        if self.iss not in allow:
            raise BearerTokenException(
                scheme='Bearer',
                error='invalid_token',
                error_description=(
                    "The access token was issued by an untrusted authorization server."
                )
            )

    def verify(
        self,
        audiences: set[str],
        issuers: set[str],
        scope: set[str] | None = None
    ):
        self.verify_audience(audiences)
        self.verify_expired()
        self.verify_issuers(issuers)
        self.verify_scope(scope or set())

    async def sign(self, signer: ITokenSigner) -> str:
        return await signer.jwt(self.dict(exclude_none=True), "at+jwt")