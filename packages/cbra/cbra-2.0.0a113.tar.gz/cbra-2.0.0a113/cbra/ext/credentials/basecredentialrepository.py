# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools

from cbra.ext.security import ApplicationKeychain
from .types import CredentialIdentifierType
from .types import GlobalCredentialIdentifier
from .types import ICredentialRepository
from .globalcredential import GlobalCredential


class BaseCredentialRepository(ICredentialRepository):
    __module__: str = 'cbra.ext.credentials'
    keychain: ApplicationKeychain

    def must_encrypt(self, credential: GlobalCredential) -> bool:
        return True

    @functools.singledispatchmethod # type: ignore
    async def get(self, credential_id: CredentialIdentifierType):
        raise TypeError(type(credential_id).__name__)
    
    async def get_global(
        self,
        credential_id: GlobalCredentialIdentifier
    ) -> GlobalCredential | None:
        raise NotImplementedError
    
    async def persist(self, credential: GlobalCredential, force: bool = False) -> None:
        dao = type(credential).parse_obj(credential.dict())
        dao.__metadata__ = credential.__metadata__
        if self.must_encrypt(credential):
            await dao.encrypt(self.keychain)
        return await self._persist(dao, force)
    
    async def persist_global(self, credential: GlobalCredential, force: bool) -> None:
        raise NotImplementedError

    @get.register # type: ignore
    async def _get_global(
        self,
        credential_id: GlobalCredentialIdentifier
    ) -> GlobalCredential | None:
        return await self.get_global(credential_id)

    @functools.singledispatchmethod
    async def _persist(self, credential: GlobalCredential, force: bool) -> None:
        raise TypeError(type(credential).__name__)
    
    @_persist.register
    async def _persist_global(self, credential: GlobalCredential, force: bool) -> None:
        return await self.persist_global(credential, force)