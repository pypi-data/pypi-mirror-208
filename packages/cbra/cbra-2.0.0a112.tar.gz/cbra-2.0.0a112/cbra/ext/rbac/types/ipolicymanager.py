# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Protocol


class IPolicyManager(Protocol):
    __module__: str = 'cbra.ext.rbac.types'

    async def attach(self, __key: Any, __policy: Any) -> None:
        """Attaches `policy` to the resource specified by `key`."""
        ...

    async def get(self, __model: Any, __key: Any) -> Any:
        ...