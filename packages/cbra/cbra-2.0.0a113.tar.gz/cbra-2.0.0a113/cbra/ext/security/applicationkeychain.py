# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Callable
from typing import TypeVar

import pydantic
from ckms.core import Keychain
from ckms.core import KeySpecification
from ckms.core import parse_dsn
from ckms.core import parse_spec

from cbra.core.conf import settings
from cbra.types import IDependant
from cbra.types import VersionedMAC
from cbra.types import VersionedCipherText


_keychain: Keychain = Keychain()
T = TypeVar('T')


class ApplicationKeychain(IDependant):
    """Provides an interface to perform cryptographic operations with
    a set of well-defined cryptographic keys.
    """
    __module__: str = 'cbra.ext.security'
    keychain: Keychain

    @staticmethod
    def load_spec(dsn: str) -> KeySpecification:
        return parse_spec(parse_dsn(dsn))

    @classmethod
    def __inject__(cls): # pragma: no cover
        return cls.setup

    @classmethod
    async def setup(cls):
        must_configure = False
        if not _keychain.has(settings.STORAGE_ENCRYPTION_KEY)\
        and settings.STORAGE_ENCRYPTION_KEY is not None:
            must_configure = True
            spec = cls.load_spec(settings.STORAGE_ENCRYPTION_KEY)
            _keychain.add(settings.STORAGE_ENCRYPTION_KEY, spec)
        if not _keychain.has(settings.STORAGE_SECURE_INDEX_KEY)\
        and settings.STORAGE_SECURE_INDEX_KEY is not None:
            must_configure = True
            spec = cls.load_spec(settings.STORAGE_SECURE_INDEX_KEY)
            _keychain.add(settings.STORAGE_SECURE_INDEX_KEY, spec)
        if must_configure:
            await _keychain
        return cls(_keychain)

    def __init__(self, keychain: Keychain) -> None:
        self.keychain = keychain

    async def create_hmac(
        self,
        value: bytes | str,
        encoding: str = 'utf-8'
    ) -> VersionedMAC:
        """Create a Hash-based Message Authentication Code (HMAC)
        using the default key.
        """
        if not isinstance(value, bytes):
            value = str.encode(value, encoding=encoding)
        k = self.keychain.get(settings.STORAGE_SECURE_INDEX_KEY)
        if k.dsn is None: # pragma: no cover
            raise ValueError("Can not use a key that is not loaded from a DSN.")
        return VersionedMAC(
            dsn=k.dsn,
            mac=await k.sign(value)
        )

    async def decrypt(
        self,
        ct: VersionedCipherText,
        parser: Callable[[VersionedCipherText, bytes], T] = lambda _, pt: pt
    ) -> T:
        k = self.keychain.get(ct.dsn)
        if k.dsn is None: # pragma: no cover
            raise ValueError("Can not use a key that is not loaded from a DSN.")
        pt = await ct.decrypt(k)
        return parser(ct, pt)

    async def encrypt(
        self,
        pt: bytes | str | pydantic.BaseModel,
        encoding: str = 'utf-8'
    ) -> VersionedCipherText:
        """Encrypt plain text `pt` using the default key."""
        k = self.keychain.get(settings.STORAGE_ENCRYPTION_KEY)
        if k.dsn is None: # pragma: no cover
            raise ValueError("Can not use a key that is not loaded from a DSN.")
        if isinstance(pt, pydantic.BaseModel):
            pt = pt.json()
        if isinstance(pt, str):
            pt = str.encode(pt, encoding=encoding)
        ct = await k.encrypt(pt)
        return VersionedCipherText(
            aad=ct.aad,
            ct=bytes(ct), # type: ignore
            iv=ct.iv,
            dsn=k.dsn,
            tag=ct.tag
        )