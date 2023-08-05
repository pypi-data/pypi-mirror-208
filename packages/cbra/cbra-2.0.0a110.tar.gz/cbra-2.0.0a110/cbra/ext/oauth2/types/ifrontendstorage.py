# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar
from typing import Protocol

from .compositeobjectidentifier import CompositeObjectIdentifier
from .objectidentifier import ObjectIdentifier


T = TypeVar('T')


class IFrontendStorage(Protocol):
    __module__: str = 'cbra.ext.oauth2.types'

    async def get(self, oid: ObjectIdentifier[T] | CompositeObjectIdentifier[T]) -> None | T: ...
    async def persist(self, obj: Any) -> None: ...