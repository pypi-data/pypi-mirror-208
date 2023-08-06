# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from cbra.types import ICache
from .cacheconfiguration import CacheConfiguration
from .memorycache import MemoryCache


__all__: list[str] = [
    'CacheConfiguration',
    'MemoryCache'
]


def cache(name: str) -> ICache:
    config = CacheConfiguration.get(name)
    async def f(impl: ICache = fastapi.Depends(config.factory)) -> ICache:
        await impl.connect(config)
        return impl
    return fastapi.Depends(f)


