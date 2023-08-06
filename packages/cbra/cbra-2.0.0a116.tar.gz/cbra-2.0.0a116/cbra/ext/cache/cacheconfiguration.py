# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Awaitable
from typing import Callable

import pydantic

from cbra.core.conf import settings
from cbra.core.ioc.loader import import_symbol
from cbra.types import ICache


class CacheConfiguration(pydantic.BaseModel):
    factory: Callable[[], Awaitable[ICache] | ICache]
    namespace: str = ''
    qualname: str

    @classmethod
    def get(cls, name: str) -> 'CacheConfiguration':
        spec = settings.CACHES.get(name)
        if spec is None:
            raise ValueError(f"No such cache: {name}")
        return cls.parse_obj(spec)
    
    @pydantic.root_validator(pre=True) # type: ignore
    def preprocess(
        cls,
        values: dict[str, str]
    ) -> dict[str, str]:
        qualname = values.get('qualname')
        if qualname is not None:
            values['factory'] = import_symbol(qualname)
        return values