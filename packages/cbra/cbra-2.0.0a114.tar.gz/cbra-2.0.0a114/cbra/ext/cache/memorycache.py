# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from cbra.types import ICache


class MemoryCache(ICache):
    __module__: str = 'cbra.ext.cache'
    objects: dict[str, Any] = {}

    def __init__(self) -> None:
        self.objects = MemoryCache.objects

    async def connect(self, config: Any) -> None:
        pass

    async def get(self, key: str) -> Any:
        return self.objects.get(key)
    
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self.objects[key] = value