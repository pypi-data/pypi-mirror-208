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
from typing import TypeVar


T = TypeVar('T', bound='IRefreshToken')


class IRefreshToken(Protocol):
    __module__: str = 'cbra.ext.oauth2.types'
    auth_time: int
    claims: dict[str, Any]
    ppid: int
    scope: set[str] | list[str]
    token: str
    sub: int

    def allows_resource(self, resource: str) -> bool: ...
    def allows_scope(self, scope: set[str]) -> bool: ...
    def is_active(self) -> bool: ...
    def refresh(self: T) -> T: ...