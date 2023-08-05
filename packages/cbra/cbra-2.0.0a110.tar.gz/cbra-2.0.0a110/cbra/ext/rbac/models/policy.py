# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import operator

import pydantic

from cbra.types import IAuthorizationContext
from cbra.types import PolicyPrincipal
from ..types import IPermissionsFinder
from .binding import Binding
from .member import Member


class Policy(pydantic.BaseModel):
    bindings: list[Binding] = pydantic.Field(
        default=[],
        title="Bindings",
        description=(
            "Associates a list of `members`, or principals, with a `role`."
        )
    )

    @property
    def members(self) -> set[Member]:
        return functools.reduce(
            operator.or_,
            [set(x.members) for x in self.bindings]
        )

    async def grants(
        self,
        finder: IPermissionsFinder,
        ctx: IAuthorizationContext
    ) -> set[str]:
        """Return the list of permissions that are granted by this
        policy.
        """
        roles: set[str] = set()
        for binding in self.bindings:
            if binding.is_conditional():
                raise NotImplementedError
            if not binding.is_satisfied(ctx):
                continue
            roles.add(binding.role)
        return await finder.get(roles)

    def add(self, role: str, member: PolicyPrincipal | str) -> None:
        """Add a member to the given binding."""
        if not isinstance(member, PolicyPrincipal):
            member = PolicyPrincipal(member)
        binding = self.get(role)
        if binding is None:
            binding = Binding(role=role)
            self.bindings.append(binding)
        if member not in binding.members:
            binding.members.append(member)

    def get(self, role: str) -> Binding | None:
        """Return the binding for the given role."""
        result = None
        for binding in self.bindings:
            if binding.role != role:
                continue
            result = binding
            break
        return result
    
    def merge(self, policy: 'Policy') -> None:
        """Merges the policies."""
        for updated in policy.bindings:
            binding = self.get(updated.role)
            if binding is None:
                binding = self.update(updated.role, set(updated.members))
                continue
            binding.update(set(updated.members))
    
    def roles(self, member: PolicyPrincipal) -> set[str]:
        return {
            binding.role for binding in self.bindings
            if binding.has(member)
        }
    
    def update(self, role: str, members: set[PolicyPrincipal | str]) -> None:
        """Add a member to the given binding."""
        for member in members:
            self.add(role, member)