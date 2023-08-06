# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable

import cbra.core as cbra
from cbra.core.conf import settings
from cbra.core.iam import NullAuthorizationContext
from cbra.types import IAuthorizationContext
from ..params import RequestAccessToken
from ..types import BearerTokenException
from ..resourceserversubjectresolver import ResourceServerSubjectResolver
from .resourceserverauthorizationcontext import ResourceServerAuthorizationContext
from .types import Scope


class ResourceServerEndpoint(cbra.Endpoint):
    __module__: str = 'cbra.ext.oauth2.endpoints'
    principal: RequestAccessToken # type: ignore
    required_scope: Iterable[Scope] = set()
    subjects: ResourceServerSubjectResolver

    def get_trusted_issuers(self) -> set[str]:
        return settings.OAUTH2_TRUSTED_ISSUERS

    async def authenticate(self) -> None:
        self.ctx = await self.setup_context()
    
    async def setup_context(self) -> IAuthorizationContext:
        if self.principal.is_anonymous():
            assert self.request.client is not None
            return NullAuthorizationContext(
                remote_host=self.request.client.host
            )
        await self.verify_token()
        await self.verify_scope()
        return ResourceServerAuthorizationContext(
            self.request,
            await self.subjects.resolve(self.principal)
        )

    async def verify_scope(self):
        granted = self.principal.get_scope()
        missing: set[str] = set()
        for scope in self.required_scope:
            missing.update(scope.missing(granted))
        if missing:
            raise BearerTokenException(
                scheme='Bearer',
                error='insufficient_scope',
                error_description=(
                    "The access token was not granted the required scope for this "
                    "resource."
                ),
                scope=missing,
                status_code=403
            )
    
    async def verify_token(self):
        await self.principal.verify(
            request=self.request,
            trusted_issuers=self.get_trusted_issuers()
        )