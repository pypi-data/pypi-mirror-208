# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import json
from typing import Any
from typing import Callable
from typing import Iterable
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client

import cbra.core as cbra
from cbra.ext.security import ApplicationKeychain
from cbra.types import PersistedModel
from cbra.types import ModelMetadata
from cbra.types import IPolymorphicCursor
from .basemodelrepository import BaseModelRepository
from .polymoprhicdatastorecursor import PolymorphicDatatoreCursor
from .types import IDatastoreKey
from .types import IDatastoreEntity

T = TypeVar('T', bound=PersistedModel)
M = TypeVar('M', bound=pydantic.BaseModel)


class PolymorphicDatastoreRepository(BaseModelRepository):
    __module__: str = 'cbra.ext.google'
    keychain: ApplicationKeychain

    def __init__(
        self,
        client: Client | Any = cbra.inject('GoogleDatastoreClient'),
        keychain: ApplicationKeychain = ApplicationKeychain.depends()
    ):
        self.client = client
        self.keychain = keychain

    def model_to_entity(self, obj: PersistedModel) -> IDatastoreEntity:
        """Convert a :class:`cbra.types.PersistedModel` to a valid
        :class:`~cbra.ext.google.types.IDatastoreEntity` implementation.
        """
        pk = self.inspect.get_primary_key_field(obj)
        if pk is None:
            raise TypeError(f'Model {type(obj).__name__} does not have a primary key.')
        key = self.model_key(obj)
        data = obj.json(exclude={pk.name})
        return self.entity_factory(key, _metadata=obj.__metadata__.dict(), **json.loads(data))

    async def auto_increment(self, obj: type[PersistedModel] | PersistedModel) -> int:
        """Return an auto incrementing integer to be used as a technical
        primary key.
        """
        return await self.allocate(self.inspect.get_entity_name(obj))

    async def find(
        self,
        cls: type[T],
        filters: list[tuple[str, str, Any]],
        ordering: list[str] | None = None
    ) -> T | None:
        """Find an entity using the given filters."""
        q = self.query(kind=cls.__name__)
        if ordering:
            q.order = ordering
        for attname, op, value in filters:
            q.add_filter(attname, op, value)
        obj: IDatastoreEntity | None = None
        for entity in (await self.run_in_executor(q.fetch)):
            if obj is not None:
                raise ValueError("Multiple objects returned")
            obj = entity
            break
        if obj is not None:
            field = self.inspect.get_primary_key_field(cls)
            assert field is not None
            return cls.parse_obj({**dict(obj), field.name: obj.key.id or obj.key.name})

    async def get(self, cls: type[T], pk: Any) -> None | T:
        """Lookup an entity by its primary key."""
        entity = await self.get_entity_by_key(self.model_key(cls, pk))
        if entity is None:
            return None
        field = self.inspect.get_primary_key_field(cls)
        assert field is not None
        return cls.parse_obj({**dict(entity), field.name: pk})


    async def get_metadata(self, key: IDatastoreKey) -> ModelMetadata | None:
        """Return the metadata for the given key, or ``None`` if there is no
        metadata.
        """
        entity = dict((await self.get_entity_by_key(key)) or {}) # type: ignore
        if entity:
            return ModelMetadata.parse_obj(entity['_metadata'])

    async def list(
        self,
        cls: type[T],
        ordering: list[str] | None = None,
        limit: int = 100,
        token: str | None = None,
        adapter: Callable[[T], M] | None = None
    ) -> IPolymorphicCursor[M]:
        query = self.query(kind=cls.__name__)
        if ordering:
            query.order = ordering
        result = await self.run_in_executor(
            functools.partial(
                query.fetch,
                start_cursor=token,
                limit=limit
            )
        )
        return PolymorphicDatatoreCursor(cls, [x for x in result], result.next_page_token, adapter=adapter) # type: ignore

    async def persist(self, obj: T) -> T:
        if not isinstance(obj, PersistedModel):
            raise TypeError(type(obj).__name__)
        entity = self.model_to_entity(obj)
        self.inspect.check_metadata(
            old=await self.get_metadata(entity.key),
            new=obj.__metadata__
        )
        await self.put(entity)
        return obj

    async def persist_many(self, objects: Iterable[T]) -> Iterable[T]:
        await self.put_multi([self.model_to_entity(x) for x in objects])
        return objects