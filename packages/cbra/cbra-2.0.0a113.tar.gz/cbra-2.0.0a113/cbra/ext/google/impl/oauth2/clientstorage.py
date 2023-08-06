# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext.oauth2 import OIDCToken

from cbra.ext.oauth2 import BaseFrontendStorage
from cbra.ext.oauth2.models import ManagedGrant
from cbra.ext.oauth2.types import AuthorizationState
from cbra.ext.oauth2.types import AuthorizationStateIdentifier
from cbra.ext.oauth2.types import ManagedGrantIdentifier
from cbra.ext.oauth2.types import OIDCTokenSubjectIdentifier
from cbra.ext.oauth2.types import ResourceAccessTokenIdentifier
from cbra.ext.oauth2.types import ResourceServerAccessToken
from .basemodelstorage import BaseModelStorage


class ClientStorage(BaseModelStorage, BaseFrontendStorage):
    __module__: str = 'cbra.ext.google.impl.oauth2'

    async def get_grant(self, oid: ManagedGrantIdentifier) -> ManagedGrant | None:
        key = self.key('ManagedGrant', str(oid))
        return self.entity_to_model(
            ManagedGrant,
            await self.get_entity_by_key(key),
            id=str(oid)
        )

    async def persist_access_token(self, obj: ResourceServerAccessToken) -> None:
        entity = self.model_to_entity(
            self.key(
                kind='ResourceServerAccessToken',
                identifier=obj.resource,
                parent=self.key('ManagedGrant', obj.grant_id)
            ),
            obj,
            exclude={'grant_id', 'resource'}
        )
        await self.put(entity)

    async def get_access_token(
        self,
        oid: ResourceAccessTokenIdentifier
    ) -> ResourceServerAccessToken | None:
        key = self.key(
            kind='ResourceServerAccessToken',
            identifier=oid.resource,
            parent=self.key('ManagedGrant', oid.grant_id)
        )
        return self.entity_to_model(
            ResourceServerAccessToken,
            await self.get_entity_by_key(key),
            grant_id=oid.grant_id,
            resource=oid.resource
        )

    async def get_authorization_state(self, oid: AuthorizationStateIdentifier) -> AuthorizationState | None:
        key = self.key('AuthorizationState', str(oid))
        return self.entity_to_model(
            AuthorizationState,
            await self.get_entity_by_key(key),
            state=oid
        )

    async def get_oidc_token(self, oid: OIDCTokenSubjectIdentifier) -> OIDCToken | None:
        key = self.key('OIDCToken', str(oid))
        return self.entity_to_model(OIDCToken, await self.get_entity_by_key(key))

    async def persist_authorization_state(self, obj: AuthorizationState) -> None:
        """Persist a :class:`~cbra.ext.oauth2.AuthorizationState` instance."""
        entity = self.model_to_entity(
            self.key('AuthorizationState', str(obj.state)),
            obj,
            exclude={'state'}
        )
        await self.put(entity)

    async def persist_grant(self, obj: ManagedGrant) -> None:
        entity = self.model_to_entity(
            self.key('ManagedGrant', obj.id),
            obj,
            exclude={'id', 'sub'}
        )
        await self.put(entity)

    async def persist_oidc_token(self, obj: OIDCToken) -> None:
        entity = self.model_to_entity(
            self.key('OIDCToken', obj.subject.sha256),
            obj,
            exclude_none=True
        )
        await self.put(entity)