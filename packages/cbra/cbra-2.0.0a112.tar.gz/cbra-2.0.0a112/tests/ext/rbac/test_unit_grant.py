# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from cbra.types import IAuthorizationContext
from cbra.types import PolicyPrincipal
from cbra.ext.rbac.models import Policy
from cbra.ext.rbac import StaticPermissionsFinder
from cbra.types.policyprincipal import PolicyPrincipal


finder: StaticPermissionsFinder = StaticPermissionsFinder(
    available={
        "foo.create",
        "foo.delete",
        "foo.get",
        "foo.list",
        "foo.update",
        "bar.create",
        "bar.delete",
        "bar.get",
        "bar.list",
        "bar.update",
        "baz.create",
        "baz.delete",
        "baz.get",
        "baz.list",
        "baz.update",
    },
    roles={
        'foo': {'foo.*'}
    }
)


class AuthorizationContext(IAuthorizationContext):

    def __init__(self, email: PolicyPrincipal):
        self.email = email

    def get_principals(self) -> set[PolicyPrincipal]:
        return {self.email}
    

@pytest.mark.asyncio
async def test_granted_by_email():
    policy = Policy()
    policy.add('foo', 'email:foo@example.com')
    ctx = AuthorizationContext(
        email=PolicyPrincipal('email:foo@example.com')
    )
    grants = await policy.grants(finder, ctx)
    assert grants == {'foo.get', 'foo.update', 'foo.list', 'foo.create', 'foo.delete'}