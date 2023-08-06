# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from cbra.core.iam.models import Subject
from .iauthorizationrequest import IAuthorizationRequest
from .iresourceowner import IResourceOwner


class BaseScope(pydantic.BaseModel):
    name: str

    def apply(
        self,
        subject: Subject,
        owner: IResourceOwner,
        claims: dict[str, Any],
        request: IAuthorizationRequest | None = None
    ) -> None:
        raise NotImplementedError

    def requires_consent(self) -> bool:
        return True
    
    def wants(self) -> tuple[set[str], set[str]]:
        """Return a tuple containing two sets of strings, where the
        first set contains the claims that a :term:`Subject` is
        required to have to satify this scope, and the second contains
        optional claims. The default implementation returns a tuple
        holding two empty sets
        """
        return (set(), set())