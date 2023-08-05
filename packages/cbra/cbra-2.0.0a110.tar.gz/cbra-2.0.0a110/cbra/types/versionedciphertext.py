# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect

import ckms.utils
import pydantic
from ckms.core import KeySpecification
from ckms.types import CipherText


class VersionedCipherText(pydantic.BaseModel):
    aad: str | None = None
    ct: str
    dsn: str
    enc: str | None = None
    iv: str | None = None
    tag: str | None = None

    @pydantic.validator('ct', 'iv', 'aad', 'tag', pre=True)
    def preprocess_bytes(cls, value: bytes | str | None) -> str | None:
        if isinstance(value, bytes):
            value = ckms.utils.b64encode_str(value)
        return value
    
    async def decrypt(self, key: KeySpecification) -> bytes:
        params: dict[str, bytes] = {}
        if self.aad: params['aad'] = ckms.utils.b64decode(self.aad)
        if self.iv: params['iv'] = ckms.utils.b64decode(self.iv)
        if self.tag: params['tag'] = ckms.utils.b64decode(self.tag)
        ct = CipherText(buf=ckms.utils.b64decode(self.ct), **params)
        result = key.decrypt(ct)
        if inspect.isawaitable(result):
            result = await result
        assert isinstance(result, bytes)
        return result
        