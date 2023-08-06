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
from typing import Generic
from typing import TypeVar

from google.cloud.datastore import Client

import cbra.core as cbra
from cbra.ext.security import ApplicationKeychain
from cbra.types import PersistedModel
from .basemodelrepository import BaseModelRepository


T = TypeVar('T', bound=PersistedModel)


class TypedDatastoreRepository(BaseModelRepository, Generic[T]):
    __module__: str = 'cbra.ext.google'
    keychain: ApplicationKeychain | None = None
    model: type[T]

    def __init__(
        self,
        client: Client | Any = cbra.inject('GoogleDatastoreClient'),
        keychain: ApplicationKeychain | None = ApplicationKeychain.depends()
    ):
        super().__init__(client=client)
        self.keychain = keychain

    async def allocate_pk(self) -> int:
        return await super().allocate(self.get_entity_name(self.model))

    async def one(
        self,
        filters: list[tuple[str, str, Any]],
        ordering: list[str] | None = None
    ) -> T | None:
        """Find a single entity using the search predicate."""
        q = self.query(kind=self.get_entity_name(self.model))
        if ordering:
            q.order = ordering
        for attname, op, value in filters:
            q.add_filter(attname, op, value)
        obj: T | None = None
        execute = functools.partial(q.fetch, limit=2)
        for entity in (await self.run_in_executor(execute)):
            if obj is not None:
                raise NotImplementedError("Multiple objects returned")
            obj = self.restore(self.model, entity)
            break
        return obj

    async def get(self, pk: int | str) -> None | T:
        """Retrieve an instance of model by its primary key, or return
        ``None`` if it does not exist.
        """
        e = await self.get_entity_by_key(self.model_key(self.model, pk=pk))
        instance = None
        if e is not None:
            instance = self.restore(self.model, e)
        return instance

    async def persist(self, obj: T, parent: PersistedModel | None = None) -> T:
        """Persist an instance of model."""
        return await self.persist_model(obj, parent=parent)