# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import warnings

from headless.ext.oauth2 import OIDCToken

import cbra.core as cbra
from cbra.types import IDependant
from cbra.types import IRequestPrincipal
from cbra.types import ISubject
from cbra.types import ISubjectResolver
from cbra.types import NullRequestPrincipal
from cbra.types import NullSubject
from cbra.types import SessionRequestPrincipal
from cbra.ext.oauth2.params import ClientStorage
from cbra.ext.oauth2.types import IFrontendStorage
from cbra.ext.oauth2.types import OIDCTokenSubjectIdentifier
from .oidcrequestsubject import OIDCRequestSubject


class FrontendSubjectResolver(ISubjectResolver, IDependant):
    __module__: str = 'cbra.core.iam'

    def __init__(
        self,
        storage: IFrontendStorage = ClientStorage
    ) -> None:
        self.storage = storage

    @functools.singledispatchmethod # type: ignore
    async def resolve(self, principal: IRequestPrincipal) -> ISubject:
        warnings.warn(
            f'{type(self).__name__} does not know how to resolve '
            f'{type(principal).__name__}, returning NullSubject.'
        )
        return NullSubject()

    @resolve.register
    async def resolve_null(
        self,
        principal: NullRequestPrincipal
    ) -> ISubject:
        return NullSubject()

    @resolve.register
    async def _resolve_session(
        self,
        principal: SessionRequestPrincipal
    ) -> ISubject:
        return await self.resolve_session(principal)

    async def resolve_session(
        self,
        principal: SessionRequestPrincipal
    ) -> ISubject:
        assert principal.claims is not None
        assert principal.subject is not None
        subject = NullSubject()
        if principal.claims.sub is not None:
            oidc = await self.storage.get(OIDCTokenSubjectIdentifier(principal.subject.sha256))
            if oidc is not None:
                subject = OIDCRequestSubject(
                    id=oidc.sub,
                    token=oidc,
                    principal=principal
                )
        return subject