# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic
from canonical import EmailAddress
from ckms.types import JSONWebKeySet
from headless.ext.oauth2.types import GrantType

from cbra.ext import secrets
from ..types import ClientAuthenticationMethod
from ..types import ClientInfo
from ..types import OIDCProvider
from ..types import PairwiseIdentifier
from ..types import RedirectURI
from ..types import RefreshTokenPolicyType
from ..types import RequestedScope
from .applicationclient import ApplicationClient


class Client(pydantic.BaseModel):
    __root__: ApplicationClient

    @property
    def access_token_ttl(self) -> int | None:
        return None

    @property
    def auth_method(self) -> ClientAuthenticationMethod:
        return self.__root__.token_endpoint_auth_method

    @property
    def client_id(self) -> str:
        return self.__root__.client_id

    @property
    def client_info(self) -> ClientInfo:
        return ClientInfo(
            allowed_email_domains=self.__root__.get_allowed_email_domains(),
            contacts=self.__root__.get_contacts(),
            id=self.__root__.client_id,
            name=self.__root__.client_name,
            organization_name=self.__root__.organization_name,
            sector_identifier=self.__root__.sector_identifier
        )

    @property
    def jwks(self) -> JSONWebKeySet | None:
        return self.__root__.jwks

    @property
    def refresh_token_policy(self) -> RefreshTokenPolicyType:
        return self.__root__.refresh_token_policy

    @property
    def refresh_token_ttl(self) -> int:
        return self.__root__.refresh_token_ttl

    @property
    def sector_identifier(self) -> str:
        return self.__root__.sector_identifier

    def allows_email(self, email: EmailAddress) -> bool:
        return True

    def allows_resources(self, resources: set[str]) -> bool:
        if self.__root__.allowed_resources is None: return True
        return resources <= set(self.__root__.allowed_resources)

    def can_grant(self, grant_type: GrantType) -> bool:
        return self.__root__.can_grant(grant_type)

    def can_redirect(self, uri: RedirectURI) -> bool:
        return self.__root__.can_redirect(uri)

    def can_use(self, scope: list[RequestedScope | str]) -> bool:
        return self.__root__.can_use(scope)

    def get_redirect_uri(self, uri: RedirectURI | None) -> RedirectURI:
        return self.__root__.get_redirect_uri(uri)
    
    def get_pairwise_identifier(self, sub: int) -> PairwiseIdentifier:
        return self.__root__.get_pairwise_identifier(sub)

    def requires_downstream(self) -> bool:
        return self.__root__.requires_downstream()
    
    def get_provider(self) -> OIDCProvider:
        return self.__root__.get_provider()

    def has_acl(self) -> bool:
        """Return a boolean indicating if the client has an ACL."""
        return self.__root__.acl.is_enabled()

    def is_confidential(self) -> bool:
        return self.auth_method != ClientAuthenticationMethod.none

    def is_member(self, obj: Any) -> bool:
        """Return a boolean indicating if the object is part of the
        ACL.
        """
        return self.__root__.acl.is_member(obj)

    async def get_client_secret(self) -> str | None:
        secret = self.__root__.client_secret
        if isinstance(secret, dict):
            container = await secrets.load(secrets.parse(**secret))
            secret = container.get_value()
        return secret