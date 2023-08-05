# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
from typing import Any
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client as GoogleClient

import cbra.core as cbra
from cbra.core.iam.models import Principal
from cbra.core.iam.models import Subject
from cbra.ext.google import DatastoreSubjectRepository
from cbra.ext.oauth2 import BaseStorage
from cbra.ext.oauth2.models import AuthorizationRequest
from cbra.ext.oauth2.models import AuthorizationRequestParameters
from cbra.ext.oauth2.models import AuthorizationState
from cbra.ext.oauth2.models import Client
from cbra.ext.oauth2.models import ExternalAuthorizationState
from cbra.ext.oauth2.models import RefreshToken
from cbra.ext.oauth2.models import ResourceOwner
from cbra.ext.oauth2.types import AuthorizationCode
from cbra.ext.oauth2.types import AuthorizationRequestIdentifier
from cbra.ext.oauth2.types import ClientIdentifier
from cbra.ext.oauth2.types import ExtAuthorizationRequestState
from cbra.ext.oauth2.types import IssuedAccessToken
from cbra.ext.oauth2.types import IssuedAccessTokenIdentifier
from cbra.ext.oauth2.types import ObjectIdentifier
from cbra.ext.oauth2.types import RefreshTokenIdentifier
from cbra.ext.oauth2.types import ResourceOwnerIdentifier
from cbra.ext.oauth2.types import PairwiseIdentifier
from cbra.ext.oauth2.types import PrincipalIdentifier
from cbra.ext.security import ApplicationKeychain
from .basemodelstorage import BaseModelStorage


T = TypeVar('T', bound=pydantic.BaseModel)


class Storage(BaseStorage, BaseModelStorage):
    __module__: str = 'cbra.ext.google.impl.oauth2'
    keychain: ApplicationKeychain
    subjects: DatastoreSubjectRepository

    def __init__(
        self,
        client: GoogleClient | Any = cbra.inject('GoogleDatastoreClient'),
        keychain: ApplicationKeychain = ApplicationKeychain.depends()
    ):
        if not isinstance(client, GoogleClient):
            raise TypeError(f"Invalid client: {repr(client)}")
        self.client = client
        self.keychain = keychain
        self.subjects = DatastoreSubjectRepository(client)

    @functools.singledispatchmethod # type: ignore
    async def destroy(self, obj: Any) -> None:
        raise TypeError(type(obj).__name__)

    @destroy.register
    async def destroy_authorization_request(
        self,
        obj: AuthorizationRequest
    ) -> None:
        await self.delete(self.key('AuthorizationRequest', obj.id))

    @destroy.register
    async def destroy_refresh_token(
        self,
        obj: RefreshToken
    ):
        await self.delete(self.key('RefreshToken', str(obj.token)))

    @functools.singledispatchmethod # type: ignore
    async def fetch(self, key: ObjectIdentifier[T]) -> Any:
        raise TypeError(type(key).__name__)

    @fetch.register
    async def fetch_authorization_request(
        self,
        oid: AuthorizationRequestIdentifier
    ) -> AuthorizationRequest | None:
        key = self.key('AuthorizationRequest', str(oid))
        return self.entity_to_model(
            AuthorizationRequest,
            await self.get_entity_by_key(key),
            id=key.name
        )

    @fetch.register
    async def fetch_authorization_request_by_code(
        self,
        oid: AuthorizationCode
    ) -> AuthorizationRequest | None:
        q = self.query(kind='AuthorizationRequest')
        q.add_filter('code.value', '=', str(oid))
        entity = await self.first(q)
        if entity:
            return self.entity_to_model(
                AuthorizationRequest,
                entity,
                id=entity.key.name
            )

    @fetch.register
    async def fetch_client(
        self,
        oid: ClientIdentifier
    ) -> Client | None:
        return None

    @fetch.register
    async def fetch_external_state(
        self,
        oid: ExtAuthorizationRequestState
    ) -> ExternalAuthorizationState | None:
        key = self.key('ExternalAuthorizationState', str(oid))
        return self.entity_to_model(
            ExternalAuthorizationState,
            await self.get_entity_by_key(key),
            id=key.name
        )

    @fetch.register
    async def fetch_issued_access_token(
        self,
        oid: IssuedAccessTokenIdentifier
    ) -> IssuedAccessToken | None:
        key = self.key('IssuedAccessToken', str(oid))
        return self.entity_to_model(
            IssuedAccessToken,
            await self.get_entity_by_key(key),
            token_hash=key.name
        )
    
    @fetch.register
    async def fetch_principal(
        self,
        oid: PrincipalIdentifier
    ) -> None | Principal:
        key = self.key('Principal', str(oid))
        return self.entity_to_model(
            Principal,
            await self.get_entity_by_key(key),
            key=str(oid)
        )

    @fetch.register
    async def fetch_refresh_token(
        self,
        oid: RefreshTokenIdentifier
    ) -> RefreshToken | None:
        key = self.key('RefreshToken', str(oid))
        return self.entity_to_model(
            RefreshToken,
            await self.get_entity_by_key(key),
            token=key.name
        )

    async def get_authorization_request_by_code(
        self,
        oid: AuthorizationCode
    ) -> AuthorizationRequestParameters | None:
        q = self.query(kind='AuthorizationRequest')
        q.add_filter('code.value', '=', str(oid))
        entity = await self.first(q)
        if entity:
            return self.entity_to_model(
                AuthorizationRequestParameters,
                entity,
                id=entity.key.name
            )

    async def get_authorization_request_by_id(
        self,
        oid: AuthorizationRequestIdentifier
    ) -> AuthorizationRequestParameters | None:
        key = self.key('AuthorizationRequest', str(oid))
        return self.entity_to_model(
            AuthorizationRequestParameters,
            await self.get_entity_by_key(key),
            id=key.name
        )

    async def get_client(self, client_id: str) -> Client | None:
        return None

    async def get_resource_owner(
        self,
        oid: ResourceOwnerIdentifier
    ) -> ResourceOwner | None:
        key = self.key('ResourceOwner', f'clients/{oid.client_id}/subjects/{oid.sub}')
        return self.entity_to_model(
            ResourceOwner,
            await self.get_entity_by_key(key),
        )

    async def persist_authorization_request(self, obj: AuthorizationRequestParameters) -> None:
        entity = self.model_to_entity(self.key('AuthorizationRequest', obj.id), obj)
        await self.put(entity)

    async def persist_issued_access_token(
        self,
        obj: IssuedAccessToken
    ) -> None:
        entity = self.model_to_entity(
            self.key(type(obj).__name__, obj.token_hash),
            obj,
            exclude={'token_hash'}
        )
        await self.put(entity)

    async def persist_state(self, obj: AuthorizationState | ExternalAuthorizationState) -> None:
        if isinstance(obj, AuthorizationState):
            raise NotImplementedError
        entity = self.model_to_entity(self.key(type(obj).__name__, obj.id), obj.__root__)
        await self.put(entity)

    async def persist_ppid(self, obj: PairwiseIdentifier) -> None:
        key = self.key(
            'PairwiseIdentifier',
            await self.allocate('PairwiseIdentifier')
        )
        entity = self.entity_factory(key)
        entity.update({'sector': obj.sector, 'sub': obj.sub})
        await self.put(entity)
        assert entity.key.id is not None
        obj.value = entity.key.id

    async def persist_refresh_token(self, obj: RefreshToken) -> None:
        # TODO: Since we havent implement the AuthorizedGrant yet,
        # simply allocate an id.
        if obj.grant_id == 0:
            obj.grant_id = await self.allocate('AuthorizedGrant')
        key = self.key('RefreshToken', str(obj.token))
        await self.put(self.model_to_entity(key, obj, exclude={'token'}))

    async def persist_resource_owner(self, obj: ResourceOwner) -> None:
        key = self.key('ResourceOwner', f'clients/{obj.client_id}/subjects/{obj.sub}')
        await self.put(self.model_to_entity(key, obj))

    async def persist_subject(self, obj: Subject) -> None:
        if not obj.is_encypted():
            await obj.encrypt(self.keychain)
        await self.subjects.persist(obj)