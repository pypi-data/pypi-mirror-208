# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.ext.credentials import BaseCredentialRepository
from cbra.ext.credentials import GlobalCredential
from cbra.ext.credentials import GlobalCredential
from cbra.ext.credentials.types import GlobalCredentialIdentifier
from ...basemodelrepository import BaseModelRepository


class DatastoreCredentialRepository(BaseModelRepository, BaseCredentialRepository):
    __module__: str = 'cbra.ext.google.impl.credentials'

    async def get_global(
        self,
        credential_id: GlobalCredentialIdentifier
    ) -> GlobalCredential | None:
        e = await self.get_entity_by_key(self.model_key(GlobalCredential, credential_id))
        c = None
        if e is not None:
            c = self.restore(GlobalCredential, e)
            c.__repository__ = self
            await c.decrypt(self.keychain)
        return c

    async def persist_global(self, credential: GlobalCredential, force: bool) -> None:
        await self.persist_model(credential, force=force)