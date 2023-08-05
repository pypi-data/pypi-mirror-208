# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse

import fastapi
from canonical import EmailAddress

import cbra.core as cbra
from cbra.core.conf import settings
from cbra.types import SessionRequestPrincipal
from ..models import AuthorizationRequestClient
from ..models import AuthorizationRequest
from ..models import ExternalAuthorizationState
from ..models import ResourceOwner
from ..params import TokenBuilder
from ..types import ResourceOwnerIdentifier
from .base import AuthorizationServerEndpoint


class AuthorizationEndpoint(AuthorizationServerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    client: AuthorizationRequestClient # type: ignore
    csrf_protect: bool = True
    metrics: cbra.MetricReporter = cbra.MetricReporter('oauth2')
    name: str = 'oauth2.authorize'
    principal: SessionRequestPrincipal # type: ignore
    path: str = '/authorize'
    status_code: int = 303
    summary: str = 'Authorization Endpoint'

    async def get(
        self,
        params: AuthorizationRequest = AuthorizationRequest.depends()
    ) -> fastapi.Response:
        await self.session
        await params.load(
            client=self.client,
            storage=self.storage,
            session_id=self.session.id
        )

        # First check if the client requires authentication with a
        # downstream provider, since the user will be authenticated
        # any way when it returns here.
        if self.client.requires_downstream() and not params.is_authenticated():
            self.session.pop('ctx')
            return await self.on_downstream_required(params)

        if not self.is_authenticated():
            self.session.pop('ctx')
            return await self.on_login_required(params)

        # Create the resource owner.
        subject = await self.get_subject()
        owner, created = await self.get_or_create_resource_owner(
            client=self.client,
            subject_id=self.session.uid
        )
        if created:
            self.logger.debug(
                "Onboarded subject to client (client: %s, "
                "sub: %s, sector: %s, ppid: %s)",
                self.client.client_id, self.session.uid,
                owner.ppid.sector, owner.ppid.value
            )

        assert self.session.uid
        email = owner.email or params.email
        if email is not None and not self.client.allows_email(email):
            raise NotImplementedError
        assert isinstance(email, EmailAddress) or email is None

        # If the Subject has multiple email addresses and no specific
        # email address was forced by the downstream authentication,
        # an email must be selected. Otherwise, the email address is
        # the email address of the Subject.
        if subject.can_select_email() and email is None:
            return await self.on_select_account(params)
        elif not subject.can_select_email():
            # At this point we may assume that the Subject has at least one
            # email address, but if it hasn't, then some error occurred
            # somehwere else and we logout the user.
            try:
                email = subject.get_email()
            except ValueError:
                return await self.on_login_required(params, logout=True)
            params.set_email(email, prompted=False)

        # Also redirect if it was explicitely requested to select and
        # account.
        if params.must_select_account():
            return await self.on_select_account(params)
        
        if self.client.has_acl() and not self.client.is_member(email):
            self.session.pop('ctx')
            self.logger.debug(
                "Resource Owner was denied access to the Application (email: %s)",
                email
            )
            return await self.on_access_denied(params)

        # TODO: The owner must consent to the audiences
        if params.resources:
            owner.resources |= params.resources
            await self.storage.persist(owner)

        # TODO: For some reason the email can be None here. For now,
        # solve this by deauthenticating the user and redirecting to
        # the login endpoint.
        if email is None:
            return await self.on_login_required(params)

        # Check if all claims required by the authorization request scope are known
        # for this Subject. If not, redirect to a web page where the Resource Owner
        # can provide these claims.
        needs = params.needs(subject) # type: ignore
        if needs:
            return await self.on_update_required(params, needs)

        # If this is an OpenID request, create the claims that will be
        # included in the ID Token so they can be displayed to the user.
        builder = TokenBuilder(self.storage, self.get_issuer(), self.client.impl)
        await params.verify(
            builder=builder,
            request=self.request,
            session=self.session.claims,
            client=self.client,
            owner=owner,
            subject=subject # type: ignore
        )
        await params.persist(self.storage) # type: ignore
        if params.must_consent():
            return await self.on_consent_required(params)

        self.delete_cookies()

        # TODO: Sometime the Subject is not activated after returning from
        # the callback endpoint.
        if not subject.is_active():
            subject.activate()
            await self.persist(subject)

        return params.as_response(client=self.client, iss=self.get_issuer())

    async def on_access_denied(self, params: AuthorizationRequest) -> fastapi.Response:
        """Invoked when the :term:`Resource Owner` is denied access based
        on ACL membership.
        """
        self.delete_cookies(exclude={'oauth2.request'})
        return fastapi.responses.RedirectResponse('/denied')

    async def on_consent_required(
        self,
        params: AuthorizationRequest
    ) -> fastapi.Response:
        """Invoked when the :term:`Resource Owner` must consent to the
        requested scope and/or claims.
        """
        q: dict[str, str] = {'next': params.get_authorize_url(self.request)}
        response = fastapi.responses.RedirectResponse(
            status_code=303,
            url=f'/consent?{urllib.parse.urlencode(q)}'
        )
        response.set_cookie(key='oauth2.request', value=params.id)
        return response

    async def on_downstream_required(
        self,
        params: AuthorizationRequest
    ) -> fastapi.Response:
        """Invoked when the end-user must authenticate with a downstream
        identity provider.
        """
        self.logger.debug(
            "Client requires downstream authentication (client_id: %s)",
            self.client.client_id
        )
        async with self.client.get_provider() as provider:
            state = ExternalAuthorizationState.new(
                provider, self.client.client_id, 'downstream', params.id, 
                params.get_authorize_url(self.request),
            )
            url = await state.get_redirect_uri(
                provider=provider,
                callback_uri=str(self.request.url_for('oauth2.callback')),
            )
        state.set_return_url(settings.OAUTH2_DOWNSTREAM_PROMPT_URL, next=url)
        assert state.return_url is not None
        response = fastapi.responses.RedirectResponse(
            status_code=303,
            url=state.return_url
        )
        response.set_cookie(key='oauth2.request', value=params.id)
        await self.storage.persist(state)
        return response

    async def on_login_required(self, params: AuthorizationRequest, logout: bool = False) -> fastapi.Response:
        """Invoked when the end-user needs to establish an authenticated
        session before proceeding with an authorization request.
        """
        if logout:
            self.session.logout()
            params.add_to_session(self.session)
            assert params.session_id == self.session.id
            await params.persist(self.storage)
        self.delete_cookies(exclude={'oauth2.request'})
        self.logger.debug("The Resource Owner must authenticate to proceed")
        p: dict[str, str] = {
            'next': params.get_authorize_url(self.request),
            'request': params.id
        }
        q = urllib.parse.urlencode(p, quote_via=urllib.parse.quote)
        response = fastapi.responses.RedirectResponse(
            status_code=303,
            url=settings.LOGIN_URL + f'?{q}'
        )
        response.set_cookie(key='oauth2.request', value=params.id)
        return response
    
    async def on_select_account(self, params: AuthorizationRequest) -> fastapi.Response:
        """Invoked when the Resource Owner must select a specific email address."""
        q: dict[str, str] = {
            'next': params.get_authorize_url(self.request),
        }
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=f'/select-account?{urllib.parse.urlencode(q)}'
        )

    async def on_update_required(
        self,
        params: AuthorizationRequest,
        needs: set[str] | None = None
    ) -> fastapi.Response:
        """Invoked when the Resource Owner must update it's profile."""
        q: dict[str, str] = {
            'next': params.get_authorize_url(self.request),
        }
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=f'/update?{urllib.parse.urlencode(q)}'
        )

    @cbra.describe(summary="Authorization Endpoint (OpenID Connect)")
    async def post(self) -> None:
        """The OpenID Connect Core specification mandates that the **Authorization
        Endpoint** must support the HTTP `POST` method. This endpoint takes the
        parameters supported by the `GET` endpoint as the request body, which
        must be provided as `application/json` or `application/x-www-form-urlencoded`.

        *This endpoint is not implemented.*
        """
        # https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        raise NotImplementedError
    
    async def get_or_create_resource_owner(
        self,
        client: AuthorizationRequestClient,
        subject_id: int
    ) -> tuple[ResourceOwner, bool]:
        created = False
        owner = await self.storage.get(
            ResourceOwner,
            ResourceOwnerIdentifier(client_id=client.client_id, sub=subject_id)
        )
        if owner is None:
            created = True
            ppid = client.get_pairwise_identifier(subject_id)
            await self.storage.persist(ppid)
            owner = ResourceOwner(
                client_id=client.client_id,
                ppid=ppid,
            )
            await self.storage.persist(owner)
            self.metrics.report('SubjectOnboarded', {
                'client_id': client.client_id,
                'sector_identifier': client.sector_identifier
            })
        return owner, created