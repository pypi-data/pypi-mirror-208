# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from canonical import EmailAddress

from ..types import PairwiseIdentifier
from ..types import ResourceOwnerIdentifier
from ..types import RequestedScope


class ResourceOwner(pydantic.BaseModel):
    client_id: str
    consents: set[str] = set()
    email: EmailAddress | None = None
    ppid: PairwiseIdentifier
    resources: set[str] = set()

    @property
    def id(self) -> ResourceOwnerIdentifier:
        return ResourceOwnerIdentifier(client_id=self.client_id, sub=self.ppid.sub)
    
    @property
    def sub(self) -> int:
        return self.ppid.sub
    
    def consent_required(self, scope: list[RequestedScope]) -> list[RequestedScope]:
        return [
            x for x in scope
            if x.name not in self.consents
            and x.requires_consent()
        ]