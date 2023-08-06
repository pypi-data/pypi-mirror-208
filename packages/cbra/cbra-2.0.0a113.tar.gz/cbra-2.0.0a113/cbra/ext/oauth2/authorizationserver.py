# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from fastapi.responses import RedirectResponse

import cbra.core as cbra
from cbra.core.conf import settings
from cbra.types import Request
from .applicationstorage import ApplicationStorage
from .authorizationrequestendpoint import AuthorizationRequestEndpoint
from .authorizationserverstorage import AuthorizationServerStorage
from .callbackendpoint import CallbackEndpoint
from .clientkeysendpoint import ClientKeysEndpoint
from .currentsubjectendpoint import CurrentSubjectEndpoint
from .endpoints import AuthorizationEndpoint
from .endpoints import AuthorizationServerEndpoint
from .endpoints import UserInfoEndpoint
from .frontendloginendpoint import FrontendLoginEndpoint
from .frontendproxyendpoint import FrontendProxyEndpoint
from .frontendredirectionendpoint import FrontendRedirectionEndpoint
from .frontenduserendpoint import FrontendUserEndpoint
from .jwksendpoint import JWKSEndpoint
from .metadataendpoint import MetadataEndpoint
from .onboardingendpoint import OnboardingEndpoint
from .server import EmailRegistrationEndpoint
from .tokenendpoint import TokenEndpoint
from .tokenhandlerendpoint import TokenHandlerEndpoint
from .types import ResponseType


class AuthorizationServer(cbra.APIRouter):
    __module__: str = 'cbra.ext.oauth2'
    client: dict[str, Any] | None | bool
    downstream: dict[str, Any] | None
    iss: str | None
    handlers: set[type[AuthorizationServerEndpoint | TokenHandlerEndpoint]] = set()
    response_types: list[ResponseType]
    storage_class: type[AuthorizationServerStorage]
    token_handler: bool = False

    def __init__(
        self,
        response_types: list[ResponseType] | None = None,
        iss: str | None = None,
        client: dict[str, Any] | None | bool = None,
        downstream: dict[str, Any] | None = None,
        storage_class: type[AuthorizationServerStorage] = AuthorizationServerStorage,
        token_handler: bool = False,
        frontend_login_endpoint: type[FrontendLoginEndpoint] = FrontendLoginEndpoint,
        oidc_onboarding_endpoint: type[OnboardingEndpoint] = OnboardingEndpoint,
        email_verification_endpoint: type[EmailRegistrationEndpoint] = EmailRegistrationEndpoint,
        current_subject_endpoint: type[CurrentSubjectEndpoint] = CurrentSubjectEndpoint,
        handlers: set[Any] | None = None,
        *args: Any,
        **kwargs: Any
    ):
        super().__init__(*args, **kwargs) # type: ignore
        self.client = client
        self.downstream = downstream
        self.iss = iss
        self.response_types = response_types or []
        self.storage_class = storage_class
        self.token_handler = token_handler

        # Determine which request handlers we must add to the authorization
        # server.
        self.handlers = handlers or set()
        if token_handler:
            self.handlers.update({
                frontend_login_endpoint,
                FrontendProxyEndpoint,
                FrontendRedirectionEndpoint,
                FrontendUserEndpoint,
                UserInfoEndpoint,
            })

        if settings.APP_ENCRYPTION_KEY and settings.APP_SIGNING_KEY:
            self.handlers.add(ClientKeysEndpoint)

        # If there is any response type, this indicates that the
        # server must provide an authorization endpoint.
        if response_types:
            self.handlers.add(AuthorizationRequestEndpoint)
            self.handlers.add(AuthorizationEndpoint)
            self.handlers.add(CallbackEndpoint)
            self.handlers.add(current_subject_endpoint)
            self.handlers.add(JWKSEndpoint)
            self.handlers.add(oidc_onboarding_endpoint)
            self.handlers.add(TokenEndpoint)
            self.handlers.add(email_verification_endpoint) # type: ignore
            self.handlers.add(UserInfoEndpoint)

    def add_to_router(self, router: cbra.Application, *args: Any, **kwargs: Any):
        self.container = router.container
        self.container.provide('_ApplicationStorage', {
            'qualname': f'{ApplicationStorage.__module__}.{ApplicationStorage.__name__}',
            'symbol': ApplicationStorage
        })
        self.container.provide('_AuthorizationServerStorage', {
            'qualname': f'{self.storage_class.__module__}.{self.storage_class.__name__}',
            'symbol': self.storage_class
        })
        self.container.provide('AuthorizationServerStorage', {
            'qualname': settings.OAUTH2_STORAGE
        })
        self.container.provide('_AuthorizationClientStorage', {
            'qualname': settings.OAUTH2_CLIENT_STORAGE
        })
        for handler in sorted(self.handlers, key=lambda x: x.__name__):
            self.add(handler, path=handler.path)

        # The metadata endpoint is a special case - its always added
        # to the root application. Also add the metadata endpoint
        # to .well-known/openid-configuration for OIDC compatibility.
        if not self.token_handler and self.response_types:
            router.add(MetadataEndpoint, path=MetadataEndpoint.path)
            router.add_api_route(
                path="/.well-known/openid-configuration",
                endpoint=self.redirect_metadata,
                include_in_schema=False,
            )

        return super().add_to_router(router, *args, **kwargs)

    async def redirect_metadata(self, request: Request) -> RedirectResponse:
        return RedirectResponse(
            status_code=303,
            url=request.url_for('oauth2.metadata')
        )