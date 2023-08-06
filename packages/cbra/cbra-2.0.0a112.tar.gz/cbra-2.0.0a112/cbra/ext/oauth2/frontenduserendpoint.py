# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext.oauth2.models import OIDCToken

from cbra.core.conf import settings
from cbra.types import NotFound
from cbra.types import SessionRequestPrincipal
from .tokenhandlerendpoint import TokenHandlerEndpoint
from .types import OIDCTokenSubjectIdentifier


class FrontendUserEndpoint(TokenHandlerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    name: str = 'bff.user'
    path: str = '/oauth/v2/user'
    principal: SessionRequestPrincipal # type: ignore
    response_model_exclude: set[str] = {
        "aud",
        "azp",
        "at_hash",
        "c_hash",
        "exp",
        "iat",
        "iss",
        "nbf",
        "nonce",
    }
    response_model_exclude_none: bool = True
    summary: str = "Current User"

    async def get(self) -> OIDCToken:
        await self.session
        if not self.session.subject:
            self.logger.debug("User is not authenticated")
            raise NotFound
        oidc = await self.storage.get(OIDCTokenSubjectIdentifier(self.session.subject.sha256))
        if oidc is None:
            self.logger.debug("No OIDC token found for authenticated user.")
            raise NotFound
        if oidc.email:
            oidc.email_verified = settings.APP_ISSUER_TRUST # TODO
        return oidc
    
    async def delete(self) -> None:
        await self.session
        self.session.logout()