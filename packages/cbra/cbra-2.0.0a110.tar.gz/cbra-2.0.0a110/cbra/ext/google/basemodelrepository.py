# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
from typing import Any
from typing import TypeVar

from cbra.types import PersistedModel
from cbra.types import ModelInspector
from cbra.types import ModelMetadata
from .basedatastorerepository import BaseDatastoreRepository
from .types import IDatastoreEntity
from .types import IDatastoreKey


T = TypeVar('T', bound=PersistedModel)


class BaseModelRepository(BaseDatastoreRepository):
    __module__: str = 'cbra.ext.google'
    inspect: ModelInspector = ModelInspector()

    def get_entity_name(self, model: type[PersistedModel] | PersistedModel) -> str:
        return self.inspect.get_entity_name(model)

    def get_primary_key(self, obj: PersistedModel) -> Any:
        """Return the primary key value of the object."""
        field = self.inspect.get_primary_key_field(obj)
        if field is None:
            raise TypeError(f'Model {type(obj).__name__} does not have a primary key.')
        return getattr(obj, field.name)

    def model_key(
        self,
        obj: type[PersistedModel] | PersistedModel,
        pk: Any | None = None,
        parent: PersistedModel | IDatastoreKey | None = None
    ) -> IDatastoreKey:
        """Return a :class:`cbra.ext.google.types.IDatastoreKey` instance
        based on the primary key of the model.
        """
        if isinstance(parent, PersistedModel):
            parent = self.model_key(parent)
        if not pk and isinstance(obj, PersistedModel):
            #if not isinstance(obj, PersistedModel):
            #    raise TypeError("The 'pk' parameter can not be None.")
            pk = self.get_primary_key(obj)
        return self.key(self.inspect.get_entity_name(obj), pk, parent=parent)


    def model_to_entity(
        self,
        obj: PersistedModel,
        key: IDatastoreKey | None = None,
        parent: PersistedModel | None = None
    ) -> IDatastoreEntity:
        """Convert a :class:`cbra.types.PersistedModel` to a valid
        :class:`~cbra.ext.google.types.IDatastoreEntity` implementation.
        """
        pk = self.inspect.get_primary_key_field(obj)
        if pk is None:
            raise TypeError(f'Model {type(obj).__name__} does not have a primary key.')
        key = key or self.model_key(obj, parent=parent)
        data = obj.json(exclude={pk.name})
        return self.entity_factory(key, _metadata=obj.__metadata__.dict(), **json.loads(data))

    async def get_metadata(self, key: IDatastoreKey) -> ModelMetadata | None:
        """Return the metadata for the given key, or ``None`` if there is no
        metadata.
        """
        entity = dict((await self.get_entity_by_key(key)) or {}) # type: ignore
        if entity:
            return ModelMetadata.parse_obj(entity['_metadata'])

    async def persist_model(self, obj: T, parent: PersistedModel | None = None) -> T:
        if not isinstance(obj, PersistedModel):
            raise TypeError(type(obj).__name__)
        entity = self.model_to_entity(obj, parent=parent)
        self.inspect.check_metadata(
            old=await self.get_metadata(entity.key),
            new=obj.__metadata__
        )
        await self.put(entity)
        return obj