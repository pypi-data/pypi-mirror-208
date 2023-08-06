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

from canonical import EmailAddress

from cbra.types import IEmailSender


T = TypeVar('T', bound='IEmailChallenge')


class IEmailChallenge(Protocol):
    @classmethod
    def new(cls: type[T], email: EmailAddress) -> T: ...
    def age(self) -> int: ...
    def get_challenge_id(self) -> str: ...
    def is_blocked(self) -> bool: ...
    def verify(self, code: str) -> bool: ...

    async def send(
        self,
        service: IEmailSender,
        sender: str,
        subject: str,
        template: str = 'email-verification.html.j2',
        context: dict[str, Any] | None = None
    ) -> None:
        ...