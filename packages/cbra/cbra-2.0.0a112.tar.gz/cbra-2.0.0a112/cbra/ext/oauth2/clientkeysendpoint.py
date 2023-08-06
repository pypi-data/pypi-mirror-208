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

from cbra.core.params import ApplicationKeychain
from .endpoints import AuthorizationServerEndpoint


class ClientKeysEndpoint(AuthorizationServerEndpoint):
    keychain: Keychain = ApplicationKeychain
    name: str = 'oauth2.client-jwks'
    status_code: int = 303
    summary: str = 'Application Client JWKS Endpoint'
    path: str = '/client-jwks.json'

    async def get(self) -> JSONWebKeySet:
        return self.keychain.as_jwks(private=False)