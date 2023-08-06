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


class SubScope(BaseScope):
    name: Literal['sub']

    def apply(
        self,
        subject: Subject,
        owner: IResourceOwner,
        claims: dict[str, Any],
        request: IAuthorizationRequest | None = None
    ) -> None:
        claims['sub'] = str(owner.ppid.value)
        claims['sct'] = owner.ppid.sector