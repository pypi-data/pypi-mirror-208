# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic
from canonical import ResourceName

from cbra.types import PersistedModel
from cbra.ext.oauth2.client import ManagedGrant
from cbra.ext.security import ApplicationKeychain
from .types import CredentialScope
from .types import ICredentialRepository


class GlobalCredential(PersistedModel):
    scope: Literal[CredentialScope.GLOBAL] = pydantic.Field(
        default=CredentialScope.GLOBAL
    )

    service: ResourceName = pydantic.Field(
        default=...,
        primary_key=True
    )

    credential: ManagedGrant = pydantic.Field(
        default=...
    )

    encrypted: bool = pydantic.Field(
        default=False
    )

    __repository__: ICredentialRepository | None = pydantic.PrivateAttr(
        default=None
    )

    async def decrypt(self, keychain: ApplicationKeychain):
        await self.credential.decrypt(keychain)
        self.encrypted = False

    async def encrypt(self, keychain: ApplicationKeychain):
        await self.credential.encrypt(keychain)
        self.encrypted = True

    async def persist(self) -> None:
        assert self.__repository__ is not None
        await self.__repository__.persist(self)