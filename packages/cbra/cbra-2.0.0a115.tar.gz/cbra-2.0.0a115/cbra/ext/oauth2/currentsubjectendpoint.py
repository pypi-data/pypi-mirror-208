# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from cbra.core.iam.types import Subject
from cbra.types import Forbidden
from .endpoints import AuthorizationServerEndpoint
from .server.endpoints.models import CurrentSubjectResponse
from .server.endpoints.models import SelfAssertedClaimsRequest


class CurrentSubjectEndpoint(AuthorizationServerEndpoint):
    name: str = 'oauth2.me'
    path: str = '/me'
    summary: str = 'Current User Endpoint'

    async def get(self) -> CurrentSubjectResponse:
        await self.session
        claims: dict[str, Any] = {
            'sub': 'allUsers',
            'mailboxes': []
        }
        if self.is_authenticated():
            claims['sub'] = 'self'
            subject = await self.get_subject()
            for principal in subject.get_principals():
                if principal.spec.kind != 'EmailAddress':
                    continue
                claims['mailboxes'].append({
                    'principal_id': principal.key,
                    'email': principal.spec.email
                })
            claims.update(subject.get_claims())

        return CurrentSubjectResponse.parse_obj(claims)
    
    async def patch(self, dto: SelfAssertedClaimsRequest) -> None:
        """Self-assert claims regarding the identity of the Subject."""
        await self.session
        if not self.is_authenticated():
            raise Forbidden
        await self.on_claims_asserted(await self.get_subject(), dto)

    async def on_claims_asserted(self, subject: Subject, dto: Any) -> None:
        self.logger.critical(
            f'{type(self).__name__}.on_claims_asserted() is not implemented.'
        )