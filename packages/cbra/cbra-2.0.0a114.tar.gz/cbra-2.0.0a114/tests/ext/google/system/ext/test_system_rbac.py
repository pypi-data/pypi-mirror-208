# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
import pytest
import pytest_asyncio
from google.cloud.datastore import Client

from cbra.ext.rbac.models import Policy
from cbra.ext.google.impl.rbac import DatastorePolicyManager
from cbra.ext.google import PolymorphicDatastoreRepository
from cbra.types import PersistedModel
from cbra.types import PolicyPrincipal


class ProtectedResource(PersistedModel):
    id: int | None = pydantic.Field(default=None, primary_key=True)
    name: str


@pytest_asyncio.fixture # type: ignore
async def manager(client: Client):
    manager = DatastorePolicyManager(client=client)
    yield manager
    q = manager.query(kind='IAMPolicy')
    for e in await manager.run_in_executor(q.fetch):
        await manager.delete(e.key)


@pytest_asyncio.fixture # type: ignore
async def resource(repo: PolymorphicDatastoreRepository):
    obj = ProtectedResource(
        id=await repo.auto_increment(ProtectedResource),
        name="Hello world!"
    )
    await repo.persist(obj)
    yield obj
    await repo.delete(repo.model_key(obj))


@pytest.mark.asyncio
async def test_attach_policy(
    manager: DatastorePolicyManager,
    resource: ProtectedResource
):
    p1 = Policy()
    p1.add("owner", "user:foo@example.com")
    await manager.attach(resource, p1)
    p2 = await manager.get(ProtectedResource, resource.id)
    assert p2 is not None
    assert p2.bindings == p1.bindings
    assert len(await manager.get_keys_by_princpal(ProtectedResource, {PolicyPrincipal("user:foo@example.com")})) == 1
    assert len(await manager.get_keys_by_princpal(ProtectedResource, {PolicyPrincipal("user:bar@example.com")})) == 0