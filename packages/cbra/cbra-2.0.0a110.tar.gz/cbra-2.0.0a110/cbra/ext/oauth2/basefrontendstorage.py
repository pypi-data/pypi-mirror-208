# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeAlias
from typing import TypeVar
from typing import Union

from headless.ext.oauth2 import OIDCToken

from .models import ManagedGrant
from .types import AuthorizationState
from .types import AuthorizationStateIdentifier
from .types import IFrontendStorage
from .types import ManagedGrantIdentifier
from .types import CompositeObjectIdentifier
from .types import ObjectIdentifier
from .types import OIDCTokenSubjectIdentifier
from .types import ResourceAccessTokenIdentifier
from .types import ResourceServerAccessToken


FrontendModel: TypeAlias = Union[
    AuthorizationState,
    ManagedGrant,
    OIDCToken,
    ResourceServerAccessToken
]

Identifier: TypeAlias = OIDCTokenSubjectIdentifier

T = TypeVar('T')


class BaseFrontendStorage(IFrontendStorage):
    __module__: str = 'cbra.ext.oauth2'
    supported_types: tuple[type, ...] = (
        AuthorizationState,
        ManagedGrant,
        OIDCToken,
        ResourceServerAccessToken,
    )

    async def get(self, oid: ObjectIdentifier[T] | CompositeObjectIdentifier[T]) -> None | T:
        if isinstance(oid, OIDCTokenSubjectIdentifier):
            return await self.get_oidc_token(oid) # type: ignore
        elif isinstance(oid, ManagedGrantIdentifier):
            return await self.get_grant(oid) # type: ignore
        elif isinstance(oid, ResourceAccessTokenIdentifier):
            return await self.get_access_token(oid) # type: ignore
        elif isinstance(oid, AuthorizationStateIdentifier):
            return await self.get_authorization_state(oid) # type: ignore

    async def get_access_token(
        self,
        oid: ResourceAccessTokenIdentifier
    ) -> ResourceServerAccessToken | None:
        raise NotImplementedError

    async def get_authorization_state(self, oid: AuthorizationStateIdentifier) -> AuthorizationState | None:
        raise NotImplementedError

    async def get_grant(self, oid: ManagedGrantIdentifier) -> ManagedGrant | None:
        raise NotImplementedError

    async def get_oidc_token(self, oid: OIDCTokenSubjectIdentifier) -> OIDCToken | None:
        raise NotImplementedError

    async def persist(self, obj: FrontendModel) -> None:
        if not isinstance(obj, self.supported_types):
            raise TypeError(type(obj).__name__)
        if isinstance(obj, AuthorizationState):
            await self.persist_authorization_state(obj)
        if isinstance(obj, ResourceServerAccessToken):
            await self.persist_access_token(obj)
        if isinstance(obj, ManagedGrant):
            await self.persist_grant(obj)
        if isinstance(obj, OIDCToken):
            await self.persist_oidc_token(obj)

    async def persist_access_token(self, obj: ResourceServerAccessToken) -> None:
        """Persist a :class:`~cbra.ext.oauth2.ResourceServerAccessToken`
        instance.
        """
        raise NotImplementedError

    async def persist_authorization_state(self, obj: AuthorizationState) -> None:
        """Persist a :class:`~cbra.ext.oauth2.AuthorizationState` instance."""
        raise NotImplementedError

    async def persist_grant(self, obj: ManagedGrant) -> None:
        """Persist a :class:`~cbra.ext.oauth2.models.ManagedGrant`
        instance.
        """
        raise NotImplementedError
    
    async def persist_oidc_token(self, obj: OIDCToken) -> None:
        """Persist a :class:`~headless.ext.oauth2.OIDCToken` instance."""
        raise NotImplementedError
        
