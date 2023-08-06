# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import TypeVar

import fastapi
from canonical import EmailAddress

import cbra.core as cbra
from cbra.types import IDependant
from ..types import ClientInfo
from ..types import FatalAuthorizationException
from ..types import IAuthorizationServerStorage
from ..types import OIDCProvider
from ..types import PairwiseIdentifier
from ..types import RedirectURI
from ..types import RequestedScope
from .client import Client


T = TypeVar('T', bound='AuthorizationRequestClient')


class AuthorizationRequestClient(IDependant):
    """An OAuth 2.x client that is requesting authorization."""
    __module__: str = 'cbra.ext.oauth2.models'
    __client: Client
    client_id: str

    @classmethod
    async def fromrequest(
        cls: type[T],
        client_id: str | None = fastapi.Query(
            default=None,
            title="Client ID",
            description="Identifies the client that is requesting authorization."
        ),
        storage: IAuthorizationServerStorage = cbra.ioc.instance('_AuthorizationServerStorage')
    ) -> T:
        if client_id is None:
            raise FatalAuthorizationException("The client_id parameter is required.")
        client = await storage.get(Client, client_id)
        if client is None:
            raise FatalAuthorizationException("The client does not exist.")
        return cls(client)

    @property
    def client_info(self) -> ClientInfo:
        return self.__client.client_info

    @property
    def impl(self) -> Client:
        return self.__client

    @property
    def sector_identifier(self) -> str:
        return self.__client.sector_identifier

    @classmethod
    def __inject__(cls: type[T]) -> Callable[..., Awaitable[T] | T]:
        return cls.fromrequest

    def __init__(self, client: Client):
        self.__client = client # type: ignore
        self.client_id = client.client_id

    def allows_email(self, email: EmailAddress) -> bool:
        return True

    def allows_resources(self, resources: set[str]) -> bool:
        return self.__client.allows_resources(resources)

    def can_use(self, scope: list[RequestedScope]) -> bool:
        return self.__client.can_use(scope)

    def can_redirect(self, uri: RedirectURI) -> bool:
        return self.__client.can_redirect(uri)

    def get_redirect_uri(self, uri: RedirectURI | None) -> RedirectURI:
        return self.__client.get_redirect_uri(uri)

    def get_pairwise_identifier(self, sub: int) -> PairwiseIdentifier:
        return self.__client.get_pairwise_identifier(sub)

    def has_acl(self) -> bool:
        return self.__client.has_acl()

    def is_member(self, obj: Any) -> bool:
        return self.__client.is_member(obj) if obj else False

    def requires_downstream(self) -> bool:
        return self.__client.requires_downstream()
    
    def get_provider(self) -> OIDCProvider:
        return self.__client.get_provider()