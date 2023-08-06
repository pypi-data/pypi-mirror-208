# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast

import pydantic

import cbra.core as cbra
from cbra.types import PersistedModel
from cbra.types import PolicyPrincipal
from cbra.ext.rbac.models import Policy
from cbra.ext.rbac.types import IPolicyManager
from ...basemodelrepository import BaseModelRepository
from ...types import IDatastoreKey


class DatastorePolicyManager(BaseModelRepository, IPolicyManager):
    __module__: str = 'cbra.ext.google.impl.rbac'

    class storage_model(PersistedModel, Policy):
        kind: str
        status: str = pydantic.Field(default='default', primary_key=True)

        class Config:
            title: str = 'IAMPolicy'

    async def attach(self, resource: PersistedModel, policy: Policy):
        """Attaches `policy` to the resource specified by `key`."""
        key = self.model_key(resource)
        await self.persist_model(
            self.storage_model.parse_obj({
                **policy.dict(),
                'kind': key.kind # type: ignore
            }),
            parent=resource
        )

    async def get(
        self,
        model: type[PersistedModel] | PersistedModel,
        id: int | str | None = None
    ) -> Policy:
        """Get the role-based access policy for the given resource."""
        k = self.model_key(self.storage_model, 'default', parent=self.model_key(model, id))
        p = Policy()
        e = await self.get_entity_by_key(k)
        if e is not None:
            p = Policy.parse_obj(e)
        return p
    
    async def get_keys_by_princpal(self, model: type[PersistedModel], principals: set[PolicyPrincipal]) -> set[IDatastoreKey]:
        q = self.query(kind=self.get_entity_name(self.storage_model))
        q.add_filter('kind', '=', self.get_entity_name(model))
        q.add_filter('bindings.members', 'IN', list(principals))

        return {
            cast(IDatastoreKey, self.client.key(*e.key.flat_path[:-2])) # type: ignore
            for e in await self.run_in_executor(q.fetch)
        }