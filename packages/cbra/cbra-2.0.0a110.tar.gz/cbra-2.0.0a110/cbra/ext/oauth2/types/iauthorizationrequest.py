# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol

from canonical import EmailAddress

from cbra.types import SessionClaims


class IAuthorizationRequest(Protocol):

    @property
    def auth_time(self) -> int | None:
        ...

    @property
    def email(self) -> EmailAddress | None:
        ...

    @property
    def email_verified(self) -> bool:
        ...

    @property
    def session(self) -> SessionClaims:
        ...

    def has_owner(self) -> bool: ...