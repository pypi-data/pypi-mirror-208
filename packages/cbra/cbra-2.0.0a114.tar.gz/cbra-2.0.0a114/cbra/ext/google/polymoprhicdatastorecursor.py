# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import TypeVar

from pydantic.fields import ModelField

from cbra.types import ModelInspector
from cbra.types import PersistedModel
from .types import IDatastoreEntity


T = TypeVar('T', bound=PersistedModel)
D = TypeVar('D')


class PolymorphicDatatoreCursor:
    inspector: ModelInspector = ModelInspector()
    items: list[PersistedModel] = []
    model: type[PersistedModel]
    primary_key: ModelField
    token: str | None

    def __init__(
        self,
        model: type[PersistedModel],
        entities: list[IDatastoreEntity],
        token: bytes | str | None = None,
        adapter: Callable[[PersistedModel], Any] | None = None
    ):
        if isinstance(token, bytes):
            token = bytes.decode(token, 'utf-8')
        self.model = model
        self.primary_key = self.inspector.get_primary_key_field(model) # type: ignore
        self.token = token
        assert self.primary_key is not None
        self.adapter = adapter or (lambda e: e)
        self.items = [self.restore(e) for e in entities]

    def restore(self, entity: IDatastoreEntity) -> Any:
        obj = self.model.parse_obj({
            **dict(entity),
            self.primary_key.name: entity.key.id or entity.key.name
        })
        return self.adapter(obj)