# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from datetime import datetime
from datetime import timezone
from typing import Any

import pydantic
from canonical import AccessCode
from canonical import EmailAddress

from cbra.types import IEmailSender
from cbra.types import PersistedModel


class EmailChallenge(PersistedModel):
    """Maintains information regarding a challenge sent to an email address
    in order to prove the ownership.
    """
    id: str = pydantic.Field(
        default_factory=lambda: secrets.token_urlsafe(48),
        primary_key=True
    )

    code: AccessCode = pydantic.Field(
        default=...
    )

    email: EmailAddress = pydantic.Field(
        default=...
    )

    requested: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed: datetime | None = pydantic.Field(
        default=None
    )

    @classmethod
    def new(cls, email: EmailAddress, **kwargs: Any):
        return cls.parse_obj({
            **kwargs,
            'code': AccessCode.new(length=6, max_attempts=3, ttl=900),
            'email': email
        })

    def age(self) -> int:
        return int((datetime.now(timezone.utc) - self.requested).total_seconds())

    def get_challenge_id(self) -> str:
        return self.id

    def is_blocked(self) -> bool:
        return self.code.is_blocked() or self.code.is_expired()

    def verify(self, code: str) -> bool:
        is_completed = self.code.verify(code)
        if is_completed:
            self.completed = datetime.now(timezone.utc)
        return is_completed
    
    async def send(
        self,
        service: IEmailSender,
        sender: str,
        subject: str,
        template: str = 'email-verification.html.j2',
        context: dict[str, Any] | None = None
    ) -> None:
        await service.send_template(
            sender=sender,
            recipients=[self.email],
            subject=subject,
            template=template,
            context={
                **(context or {}),
                'access_code': self.code.secret,
            }
        )