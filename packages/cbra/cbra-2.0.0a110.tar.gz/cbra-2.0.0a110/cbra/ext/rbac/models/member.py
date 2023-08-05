# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from cbra.types import PolicyPrincipal


class Member(pydantic.BaseModel):
    role: str = pydantic.Field(
        default=...,
        title="Role",
        description=(
            "Role that is assigned to `member`, or principal. "
            "For example, `roles/viewer`, `roles/editor`, or `roles/owner`."
        )
    )

    member: PolicyPrincipal = pydantic.Field(
        default=...,
        title="Member",
        description="The principal to which the `role` is granted."
    )