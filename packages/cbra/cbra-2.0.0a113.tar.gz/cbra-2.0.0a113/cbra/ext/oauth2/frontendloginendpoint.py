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

from cbra.core.conf import settings
from cbra.types import Forbidden
from .danceinitiationmixin import DanceInitiationMixin
from .models import FrontendLoginRequest
from .models import FrontendLoginResponse
from .tokenhandlerendpoint import TokenHandlerEndpoint


class FrontendLoginEndpoint(TokenHandlerEndpoint, DanceInitiationMixin):
    __module__: str = 'cbra.ext.oauth2'
    name: str = 'bff.login'
    path: str = '/oauth/v2/login'
    redirection_endpoint: str = 'bff.redirection'
    status_code: int = 303
    summary: str = 'Frontend Login Endpoint'

    def can_redirect(self, redirect_uri: str) -> bool:
        """Return a boolean if the user-agent may request a redirect to the
        given URI.
        """
        p = urllib.parse.urlparse(redirect_uri)
        return any([
            str.startswith(redirect_uri, '/'),
            all([
                p.netloc == self.request.url.netloc,
                p.scheme == self.request.url.scheme,
            ]),
            p.netloc in settings.LOGIN_AUTHORIZED_DOMAINS
        ])
    
    def get_resources(self) -> set[str]:
        return {spec['resource'] for spec in settings.OAUTH2_RESOURCE_SERVERS.values()}

    async def get(self) -> FrontendLoginResponse:
        """Retrieve an OIDC ID Token from the trusted authorization
        server to establish the identity of the caller.
        """
        return await self.redirect_user_agent('/', {'email', 'openid', 'profile'})
    
    async def redirect_user_agent(self, redirect_uri:str, scope: set[str], **params: Any) -> FrontendLoginResponse:
        if not self.can_redirect(redirect_uri):
            raise Forbidden
        scope = scope or {'email', 'openid', 'profile'}
        url, state, nonce = await self.create_authorization_request(
            scope=scope,
            access_type='offline',
            resources=self.get_resources(),
            **params
        )
        self.set_cookie('nonce', nonce, httponly=True, secure=True)
        self.set_cookie('scope', str.join(' ', sorted(scope)), httponly=True, secure=True)
        self.set_cookie('state', state, httponly=True, secure=True)
        self.set_cookie('redirect_uri', redirect_uri, httponly=True, secure=True)
        return FrontendLoginResponse(redirect_to=url)

    async def post(self, dto: FrontendLoginRequest) -> FrontendLoginResponse:
        """Retrieve an OIDC ID Token from the trusted authorization
        server to establish the identity of the caller.
        """
        extra = dto.dict(
            include={'prompt'},
            exclude_none=True
        )
        return await self.redirect_user_agent(dto.redirect_uri, dto.scope, **extra)