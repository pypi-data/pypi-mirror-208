# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import timedelta
from typing import Any
from typing import Protocol


class IStorageBucket(Protocol):
    __module__: str = 'cbra.types'

    async def blob(self, path: str) -> Any:
        ...

    async def generate_signed_url(
        self,
        path: str,
        expires: timedelta | None = None,
        ttl: int | None = None,
        *args: Any,
        **kwargs: Any
    ) -> str:
        ...