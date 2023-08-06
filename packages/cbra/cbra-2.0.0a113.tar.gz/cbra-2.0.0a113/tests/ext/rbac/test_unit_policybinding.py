# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.types import PolicyPrincipal
from cbra.ext.rbac.models import Policy


def test_add_member_to_policy():
    policy = Policy()
    policy.add("editor", "foo")
    assert policy.roles(PolicyPrincipal("foo")) == {"editor"}
    assert len(policy.members) == 1


def test_add_member_does_not_create_duplicates():
    policy = Policy()
    policy.add("editor", "foo")
    policy.add("editor", "foo")
    binding = policy.get("editor")
    assert binding is not None
    binding.update({PolicyPrincipal("foo")})
    assert len(binding.members) == 1
    assert len(policy.members) == 1


def test_merge_x_y():
    p1 = Policy()
    p1.add("editor", "foo")
    p2 = Policy()
    p2.add("owner", "foo")
    p1.merge(p2)
    assert p1.roles(PolicyPrincipal("foo")) == {"editor", "owner"}


def test_merge_existing():
    p1 = Policy()
    p1.add("editor", "foo")
    p2 = Policy()
    p2.add("editor", "bar")
    p1.merge(p2)
    assert p1.roles(PolicyPrincipal("bar")) == {"editor"}
    assert p1.roles(PolicyPrincipal("foo")) == {"editor"}


def test_get():
    p = Policy()
    p.add("foo", "foo")
    assert p.get("foo") is not None