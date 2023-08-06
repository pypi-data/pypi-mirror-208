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

from cbra.ext.google import TypedDatastoreRepository
from cbra.types import PersistedModel
from cbra.types import VersionConflict


class TypedEntity(PersistedModel):
    id: int = pydantic.Field(default=..., primary_key=True)
    name: str


class TypedEntityRepository(TypedDatastoreRepository[TypedEntity]):
    model = TypedEntity


@pytest.fixture
def repo(client: Client):
    return TypedEntityRepository(client=client)


@pytest_asyncio.fixture # type: ignore
async def resource(repo: TypedEntityRepository):
    obj = TypedEntity(
        id=await repo.allocate_pk(),
        name="Hello world!"
    )
    await repo.persist(obj)
    yield obj
    await repo.delete(repo.model_key(obj))


@pytest.mark.asyncio
async def test_find_by_pk(
    repo: TypedEntityRepository,
    resource: TypedEntity
):
    obj = await repo.get(resource.id)
    assert obj is not None
    assert obj.id == resource.id
    assert obj.name == resource.name


@pytest.mark.asyncio
async def test_find_by_filters(
    repo: TypedEntityRepository,
    resource: TypedEntity
):
    obj = await repo.one([('name', '=', 'Hello world!')])
    assert obj is not None
    assert obj.id == resource.id
    assert obj.name == resource.name


@pytest.mark.asyncio
async def test_persist(
    repo: TypedEntityRepository,
    resource: TypedEntity
):
    o1 = await repo.get(resource.id)
    assert o1 is not None

    o1.name = "Foo"
    await repo.persist(o1)

    o2 = await repo.get(resource.id)
    assert o2 is not None
    assert o1.id == o2.id
    assert o2.name == "Foo"



@pytest.mark.asyncio
async def test_persist_concurrent(
    repo: TypedEntityRepository,
    resource: TypedEntity
):
    assert resource.__metadata__.generation == 1
    o1 = await repo.get(resource.id)
    assert o1 is not None
    assert o1.__metadata__.generation == 1

    o1.name = "Foo"
    assert o1 == await repo.persist(o1)
    assert o1.__metadata__.generation == 2
    assert resource.__metadata__.generation == 1

    resource.name = "Bar"
    with pytest.raises(VersionConflict):
        await repo.persist(resource)

    o1.name = "Baz"
    await repo.persist(o1)
    assert o1.__metadata__.generation == 3