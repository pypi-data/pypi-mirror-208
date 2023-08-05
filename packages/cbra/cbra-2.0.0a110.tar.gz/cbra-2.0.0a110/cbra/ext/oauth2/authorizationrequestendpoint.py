# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
from headless.ext.oauth2.models import ClaimSet

from cbra.types import NotFound
from cbra.types import SessionRequestPrincipal
from .endpoints import AuthorizationServerEndpoint
from .models import AuthorizationRequest
from .models import CurrentAuthorizationRequest
from .models import PatchAuthorizationRequest
from .models import PatchAuthorizationResponse
from .types import AuthorizationRequestIdentifier
from .types import ClientIdentifier
from .types import RedirectURI
from .types import PrincipalIdentifier


class AuthorizationRequestEndpoint(AuthorizationServerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    name: str = 'oauth2.authorize'
    principal: SessionRequestPrincipal # type: ignore
    path: str = '/requests'
    request_id: AuthorizationRequestIdentifier | None = fastapi.Cookie(
        default=None,
        title="Request ID",
        alias='oauth2.request',
        description=(
            "The authorization request identifier. This cookie is set by the "
            "authorization endpoint in the case that the resource owner "
            "needs to perform a certain action."
        )
    )
    summary: str = 'Authorization Request'

    async def get_authorization_request(
        self,
        request_id: AuthorizationRequestIdentifier | None
    ) -> AuthorizationRequest:
        if not request_id:
            raise NotFound
        await self.session
        request = await self.storage.get(AuthorizationRequest, request_id)
        if request is None:
            self.logger.debug("Authorization request does not exist")
            raise NotFound
        if request.session_id != self.session.id:
            self.logger.debug(
                "Authorization request lookup by unknown session (expected: %s, actual: %s)",
                request.session_id, self.session.id
            )
            raise NotFound
        return request

    async def get(
        self,
        query_request_id: AuthorizationRequestIdentifier | None = fastapi.Query(
            default=None,
            title="Request ID",
            alias="request_id",
            description=("The authorization request identifier.")
        )
    ) -> CurrentAuthorizationRequest:
        request = await self.get_authorization_request(query_request_id or self.request_id)
        requires: set[str] = set()
        if self.is_authenticated():
            requires = request.needs(await self.get_subject()) # type: ignore
        return CurrentAuthorizationRequest(
            request_id=request.id,
            client=request.client_info,
            consent=request.consent,
            email=request.email,
            scope=request.scope,
            id_token=ClaimSet.parse_obj({'sub': '0', **request.id_token}),
            requires=requires
        )
    
    async def patch(
        self,
        dto: PatchAuthorizationRequest,
        query_request_id: AuthorizationRequestIdentifier | None = fastapi.Query(
            default=None,
            title="Request ID",
            alias="request_id",
            description=("The authorization request identifier.")
        )
    ) -> PatchAuthorizationResponse:
        request = await self.get_authorization_request(query_request_id or self.request_id)
        url = None
        if dto.deny:
            redirect_uri = RedirectURI(request.redirect_uri)
            url = redirect_uri.redirect(error='access_denied')
        elif dto.email:
            principal = await self.storage.fetch(PrincipalIdentifier(dto.email))
            if principal is None or not principal.is_owned_by(self.session.uid):
                raise NotFound
            request.set_email(str(principal), prompted=True)
            url = RedirectURI(request.get_authorize_url(self.request))
        elif dto.logout:
            await self.session
            client = await self.storage.fetch(ClientIdentifier(request.client_id))
            self.session.logout()
            request = request.clone()
            await request.load(client, self.storage, self.session.id)
            url = RedirectURI(request.get_authorize_url(self.request))
        else:
            raise NotImplementedError
        assert url is not None
        await request.persist(self.storage)
        return PatchAuthorizationResponse(next=url)