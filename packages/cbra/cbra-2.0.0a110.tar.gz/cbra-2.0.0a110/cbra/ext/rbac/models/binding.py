# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from cbra.types import IAuthorizationContext
from cbra.types import PolicyPrincipal
from .condition import Condition


class Binding(pydantic.BaseModel):
    role: str = pydantic.Field(
        default=...,
        title="Role",
        description=(
            "Role that is assigned to the list of `members`, or principals. "
            "For example, `roles/viewer`, `roles/editor`, or `roles/owner`."
        )
    )

    members: list[PolicyPrincipal] = pydantic.Field(
        default=[],
        title="Members",
        description=(
            "Specifies the principals requesting access for a resource. "
            "The `members` array can have the following values:\n\n"
            "- **user:{email}**: an email address that is associated to "
            "a specific account."
        )
    )

    condition: Condition | None = pydantic.Field(
        default=None,
        title="Condition",
        description=(
            "The condition that is associated with this binding.\n\n"
            "If the condition evaluates to `true`, then this binding "
            "applies to the current request.\n\n"
            "If the condition evaluates to `false`, then this binding "
            "does not apply to the current request. However, a different "
            "role binding might grant the same role to one or more "
            "of the principals in this binding.\n\n"
        )
    )

    def has(self, member: PolicyPrincipal):
        """Return a boolean indicating if this binding has the given member."""
        return member in self.members

    def is_conditional(self) -> bool:
        """Return a boolean indicating if the binding is conditional."""
        return self.condition is not None

    def is_satisfied(self, ctx: IAuthorizationContext) -> bool:
        """Return a boolean if the binding is satisfied by the authorization
        context.
        """
        if self.condition:
            raise NotImplementedError
        return any([self.has(p) for p in ctx.get_principals()])

    def update(self, members: set[PolicyPrincipal]):
        """Updates the :class:`Binding` with the given members."""
        for member in members:
            if self.has(member):
                continue
            self.members.append(member)
