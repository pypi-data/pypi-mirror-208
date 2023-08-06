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
from .subscope import SubScope
from .subjectclaimscope import SubjectClaimScope


INCLUDED_SCOPE: list[SubScope | SubjectClaimScope] = [
    SubScope(name='sub'),
    SubjectClaimScope(name='name'),
    SubjectClaimScope(name='given_name'),
    SubjectClaimScope(name='middle_name'),
    SubjectClaimScope(name='family_name'),
    SubjectClaimScope(name='nickname'),
    SubjectClaimScope(name='picture'),
    SubjectClaimScope(name='updated_at')
]

class ProfileScope(BaseScope):
    name: Literal['profile']

    def apply(
        self,
        subject: Subject,
        owner: IResourceOwner,
        claims: dict[str, Any],
        request: IAuthorizationRequest | None = None
    ) -> None:
        for scope in INCLUDED_SCOPE:
            scope.apply(
                subject=subject,
                owner=owner,
                claims=claims,
                request=request
            )

    def wants(self) -> tuple[set[str], set[str]]:
        return (
            {"birthdate", "cor", "given_name", "family_name", "name_order", "zoneinfo"},
            {"middle_name", "nickname", "picture"}
        )