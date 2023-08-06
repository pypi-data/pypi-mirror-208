# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from cbra.ext.rbac import StaticPermissionsFinder


@pytest.mark.asyncio
async def test_get_single():
    finder = StaticPermissionsFinder(
        available={'foo'},
        roles={'viewer': {'foo'}}
    )
    assert {'foo'} == await finder.get({'viewer'})


@pytest.mark.parametrize("available", [
    {'bar.get', 'bar.list', 'foo.get', 'foo.list'}
])
@pytest.mark.parametrize("roles,permissions", [
    ({"viewer"}, {"foo.get", "foo.list"}),
    ({"editor"}, {"foo.create", "foo.delete", "foo.get", "foo.list", "foo.update"}),
    ({"anonymous"}, set()), # type: ignore
    ({"role1", "role2"}, {"foo.get", "foo.list"}),
    ({"owner"}, {"bar.get", "bar.list", "foo.get", "foo.list"}),
    ({"wildcard"}, {"foo.get", "bar.get"}),
])
@pytest.mark.asyncio
async def test_get(available: set[str], roles: set[str], permissions: set[str]):
    finder = StaticPermissionsFinder(
        available=available,
        roles={
            'viewer': {
                'foo.get',
                'foo.list',
            },
            'editor': {
                'foo.create',
                'foo.delete',
                'foo.get',
                'foo.list',
                'foo.update',
            },
            'role1': {
                "foo.get",
            },
            'role2': {
                "foo.list",
            },
            'owner': {'*'},
            'wildcard': {'*.get'}
        }
    )
    assert permissions == await finder.get(roles)