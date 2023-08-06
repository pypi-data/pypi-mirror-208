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

import fastapi
from canonical import EmailAddress
from headless.ext.oauth2.models import OIDCToken
from headless.ext.oauth2.models import TokenResponse

from cbra.core.conf import settings
from cbra.core.iam.types import Subject
from cbra.types import SessionRequestPrincipal
from .const import ALLOWED_DOMAINS
from .endpoints import AuthorizationServerEndpoint
from .params import Error
from .params import DownstreamError
from .params import DownstreamTokenResponse
from .params import LocalStorageAuthorizationRequest
from .params import LocalAuthorizationRequestState
from .params import LocalOpenIdProvider
from .types import FatalAuthorizationException
from .types import IAuthorizationRequest
from .types import IExternalAuthorizationState
from .types import OIDCProvider
from .types import UserError


class CallbackEndpoint(AuthorizationServerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    authnreq: IAuthorizationRequest = LocalStorageAuthorizationRequest
    error: Error | None = DownstreamError
    name: str = 'oauth2.callback'
    state: IExternalAuthorizationState = LocalAuthorizationRequestState
    status_code: int = 303
    summary: str = 'Callback Endpoint'
    path: str = '/callback'
    principal: SessionRequestPrincipal # type: ignore
    provider: OIDCProvider = LocalOpenIdProvider
    token: TokenResponse = DownstreamTokenResponse

    def is_allowed_domain(self, email: EmailAddress | None) -> bool:
        """Return a boolean indicating if the email may be used as a recovery
        email.
        """
        return (email is not None and email.domain in ALLOWED_DOMAINS) or False

    def is_local_provider(self, provider: str) -> bool:
        return provider in {x.get('name') for x in settings.OAUTH2_CLIENTS}

    async def get(self) -> fastapi.Response:
        """The redirection endpoint for downstream identity providers."""
        await self.session
        try:
            return await self.handle()
        except Exception:
            self.delete_cookies()
            raise

    async def handle(self) -> fastapi.Response:
        ctx = self.state.kind
        if self.error:
            raise self.error
        if not self.token.id_token:
            raise FatalAuthorizationException(
                "The downstream authorization server did not include "
                "an OIDC ID Token in the response."
            )
        await self.session
        try:
            oidc = self.token.id_token.parse()
            # TODO
            assert oidc.email is not None
            oidc.email_verified = self.provider.is_trusted_email(oidc.email)
        except Exception as e:
            self.logger.exception('Caught fatal %s', type(e).__name__)
            raise FatalAuthorizationException(
                "The OIDC ID Token returned by the authorization server "
                "was malformed, invalid or otherwise unusable."
            )
        self.logger.debug("Receiving OIDC token from %s", oidc.iss)
        self.logger.debug("Trust OP-asserted email %s: %s", str(oidc.email), oidc.email_verified)
        if ctx:
            self.logger.debug("Handling callback for %s", ctx)
        if ctx == 'set-recovery':
            self.logger.debug("Handling token for recovery email")
            return await self.handle_set_recovery(oidc)

        # This is a normal downstream authentication.
        return await self.handle_authenticated(await self.get_subject(), oidc)\
            if self.is_authenticated()\
            else await self.handle_unauthenticated(oidc)

    async def handle_authenticated(
        self,
        subject: Subject,
        oidc: OIDCToken,
        was_registered: bool = False,
        was_authenticated: bool = False
    ) -> fastapi.Response:
        if not was_authenticated\
        and not all(map(subject.has_principal, oidc.principals)):
            # If the Subject was not authentcated during this request, verify
            # that it may use the token.
            if not await self.onboard.can_use(subject, oidc.principals):
                raise UserError(
                    error='identity_unusable',
                    request_id=self.authnreq.id,
                    authorize=self.authnreq.get_authorize_url(self.request)
                )
            await self.onboard.update_oidc(subject, oidc)

        # Add the token to the request so we can later determine that
        # it did an upstream authentication.
        if not self.authnreq.is_authenticated():
            self.authnreq.authenticate(oidc)
            await self.authnreq.persist(self.storage) # type: ignore
            self.logger.debug(
                "Authenticated Authorization Request (id: %s, email: %s)",
                self.authnreq.id, oidc.email
            )

        if subject.needs_fallback_email(ALLOWED_DOMAINS):
            error = 'invalid_email'
            provider = self.provider.name
            if was_authenticated:
                # If the user was registered using this token, then don't
                # display the error page.
                error = None
            if not self.is_local_provider(provider):
                provider = None
            return await self.on_fallback_email_required(subject, oidc, error, provider=provider)
        return await self.on_success(subject, oidc)

    async def handle_set_recovery(self, oidc: OIDCToken) -> fastapi.Response:
        if not self.is_authenticated():
            raise FatalAuthorizationException("Stop probing our system.")
        subject = await self.get_subject()

        # A recovery email may only be of a domain that we accept. If
        # receiving an OIDC token for use as a recovery email, therefore
        # check if the domain is accepted.
        is_acceptable = all([
            oidc.email,
            oidc.email_verified,
            self.is_allowed_domain(oidc.email),
            await self.onboard.can_use(oidc)
        ])
        if not is_acceptable:
            self.logger.debug(
                "Unacceptable email address for recovery: %s (verified: %s)",
                oidc.email, oidc.email_verified
            )
            return await self.on_fallback_email_required(
                subject, oidc, 'invalid_email',
                provider=self.provider.name
            )
        
        # At this point we have ensured that the principals enclosed in the token
        # are in use by zero or one subject. We proceed to find out that, if these
        # are owned by 1 subject, this is the same as the currently authenticated
        # subject. If they differ, and one or both of them can be destroyed, the
        # entities are merged.
        owner = await self.onboard.get(oidc)
        destroy: Subject | None = None
        if owner is None:
            # This is the happy flow. Add the principals to the existing subject
            # and proceed.
            await self.onboard.update_oidc(subject, oidc)
            subject.activate() 
            self.logger.debug(
                "Added principals from OIDC token to Subject, destroying existing (id: %s)",
                subject.uid
            )
        elif owner.uid == subject.uid:
            # For some reason we ended up here, probably because of ledtover
            # cookies (TODO).
            subject.activate()
        elif all([owner.can_destroy(), subject.can_destroy()]):
            # Both are not active. Merge the existing into the authenticated and
            # destroy the existing.
            self.logger.debug(
                "Merging inactive principals (authenticated: %s, existing: %s)",
                subject.uid, owner.uid
            )
            subject.merge(owner)
            subject.activate()
            destroy = owner
            pass
        elif subject.can_destroy():
            # In this case, merge the Subjects and update the session with the existing
            # subject and destroy the authenticated.
            owner.merge(subject)
            self.session.authenticate(owner)
            destroy = subject
            subject = owner
            subject.activate()
        elif owner.can_destroy():
            # Same as above, but other way around.
            subject.merge(owner)
            subject.activate()
            destroy = owner
        else:
            # Error
            return await self.on_identity_unusable(oidc, 'invalid_subject')

        assert not subject.can_destroy()
        assert subject.is_active()
        if destroy is not None:
            assert destroy.uid is not None
            await self.onboard.destroy(destroy.uid)
        await self.onboard.persist(subject)
        return await self.on_success(subject, oidc)

    async def handle_unauthenticated(self, oidc: OIDCToken) -> fastapi.Response:
        self.logger.debug(
            "Authenticating session with OIDC token (iss: %s, email: %s)",
            oidc.iss, oidc.email
        )
        if not await self.onboard.can_use(oidc):
            return await self.on_identity_unusable(oidc, 'forbidden')
        subject, created = await self.register(oidc)
        self.session.authenticate(subject)
        assert self.session.uid is not None
        assert self.session.is_dirty()
        self.logger.debug(
            "Authenticated Session (id: %s, uid: %s)",
            self.session.id, self.session.uid
        )
        return await self.handle_authenticated(subject, oidc, created, True)

    async def on_fallback_email_required(
        self,
        subject: Subject,
        oidc: OIDCToken,
        error: str | None = None,
        provider: str | None = None,
        **extra: Any
    ) -> fastapi.Response:
        p: dict[str, str] = {
            'next': self.authnreq.get_authorize_url(self.request),
            'request': self.authnreq.id
        }
        if error is not None:
            p.update({
                'error': error,
            })
        if provider is not None:
            p.update({
                'provider': provider,
            })
        p.update(extra)
        q = urllib.parse.urlencode(p, quote_via=urllib.parse.quote)
        self.delete_cookies(exclude={'oauth2.request'})
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=settings.OAUTH2_RECOVERY_EMAIL_URL + f'?{q}'
        )

    async def on_identity_unusable(self, oidc: OIDCToken, error: str) -> fastapi.Response:
        self.logger.debug(
            "The given identity is not usable (iss: %s, email: %s, error: %s)",
            oidc.iss, oidc.email, error
        )
        raise FatalAuthorizationException(
            "The identity provided by the authorization server is "
            "not accepted."
        )

    async def on_registered(self, subject: Subject, oidc: OIDCToken) -> None:
        self.logger.info(
            "Registered a new Subject using OIDC (id: %s, iss: %s)",
            subject.uid, oidc.iss[:64]
        )

    async def on_success(
        self,
        subject: Subject,
        oidc: OIDCToken
    ) -> fastapi.Response:
        self.delete_cookies(exclude={'oauth2.request'})
        self.logger.debug(
            "Authenticated Subject via OIDC (iss: %s, sub: %s, email: %s, verified: %s)",
            oidc.iss, subject.uid, oidc.email, oidc.email_verified
        )
        self.session.set('email', oidc.email)
        self.session.set('email_verified', oidc.email_verified)

        # Update the Subject with the received claims, but do not
        # overwrite existing claims.
        subject.update_oidc(oidc)
        await self.persist(subject)
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=self.authnreq.get_authorize_url(self.request)
        )

    async def register(self, oidc: OIDCToken) -> tuple[Subject, bool]:
        subject, created = await self.onboard.oidc(oidc)
        if created:
            await self.on_registered(subject, oidc)

        return subject, created