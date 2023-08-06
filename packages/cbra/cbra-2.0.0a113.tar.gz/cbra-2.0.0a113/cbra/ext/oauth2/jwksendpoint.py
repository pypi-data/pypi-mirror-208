# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ckms.core import Keychain
from ckms.types import JSONWebKeySet

from .endpoints import AuthorizationServerEndpoint
from .params import ServerKeychain


class JWKSEndpoint(AuthorizationServerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    keychain: Keychain = ServerKeychain
    name: str = 'oauth2.jwks'
    path: str = '/jwks.json'
    status_code: int = 200
    summary: str = 'JWKS Endpoint'
    tags: list[str] = ['OAuth 2.x/OpenID Connect']

    async def get(self) -> JSONWebKeySet:
        return self.keychain.as_jwks(private=False)