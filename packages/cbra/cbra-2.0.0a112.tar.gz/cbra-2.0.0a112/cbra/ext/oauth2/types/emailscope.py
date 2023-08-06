# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

from cbra.core.iam.models import Subject
from .basescope import BaseScope
from .iauthorizationrequest import IAuthorizationRequest
from .iresourceowner import IResourceOwner


class EmailScope(BaseScope):
    name: Literal['email']

    def apply(
        self,
        subject: Subject,
        owner: IResourceOwner,
        claims: dict[str, Any],
        request: IAuthorizationRequest | None = None
    ) -> None:
        if request is not None:
            claims['email'] = request.email
            claims['email_verified'] = request.email_verified

    def wants(self) -> tuple[set[str], set[str]]:
        return (
            {"email"},
            set()    
        )