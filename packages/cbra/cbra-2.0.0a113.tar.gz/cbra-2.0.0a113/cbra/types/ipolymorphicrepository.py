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
from typing import Iterable
from typing import Protocol
from typing import TypeVar

import pydantic

from .ipolymorphiccursor import IPolymorphicCursor
from .ipolymorphicquery import IPolymorphicQuery
from .persistedmodel import PersistedModel


T = TypeVar('T', bound=PersistedModel)
M = TypeVar('M', bound=pydantic.BaseModel)


class IPolymorphicRepository(Protocol):
    __module__: str = 'cbra.types'

    async def auto_increment(self, obj: type[PersistedModel] | PersistedModel) -> int:
        """Return an auto incrementing integer to be used as a technical
        primary key.
        """
        ...

    async def find(
        self,
        cls: type[T],
        filters: list[tuple[str, str, Any]],
        ordering: list[str] | None = None,
    ) -> None | T:
        ...

    async def list(
        self,
        cls: type[T],
        ordering: list[str] | None = None,
        limit: int = 100,
        token: str | None = None,
        adapter: Callable[[T], M] | None = None
    ) -> IPolymorphicCursor[M]:
        ...
    async def query(self, cls: type[T]) -> IPolymorphicQuery[T]: ...
    async def get(self, cls: type[T], pk: Any) -> None | T: ...
    async def persist(self, obj: T) -> T: ...
    async def persist_many(self, obj: Iterable[T]) -> Iterable[T]: ...