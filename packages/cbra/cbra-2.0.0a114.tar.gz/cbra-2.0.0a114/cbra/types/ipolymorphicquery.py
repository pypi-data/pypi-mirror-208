# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

from .persistedmodel import PersistedModel


T = TypeVar('T', bound=PersistedModel, covariant=True)


class IPolymorphicQuery(Protocol, Generic[T]):

    def filter(self, param: str, operator: str, value: Any): ...