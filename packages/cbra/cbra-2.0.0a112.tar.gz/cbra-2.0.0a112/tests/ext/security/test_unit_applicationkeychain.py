# Copyright (C) 2021-2023 Cochise Ruhulessin
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

from cbra.ext.security import ApplicationKeychain


@pytest_asyncio.fixture # type: ignore
async def keychain() -> ApplicationKeychain:
    return await ApplicationKeychain.setup()


@pytest.mark.asyncio
async def test_encrypt_decrypt_bytes(
    keychain: ApplicationKeychain,
):
    pt = b"foo"
    ct = await keychain.encrypt(pt)
    dt = await keychain.decrypt(ct)
    assert pt == dt


@pytest.mark.asyncio
async def test_encrypt_decrypt_model(
    keychain: ApplicationKeychain,
):
    class Model(pydantic.BaseModel):
        foo: str
        bar: int

    pt = Model(foo='foo', bar=1)
    ct = await keychain.encrypt(pt)
    dt = await keychain.decrypt(ct, parser=lambda _, pt: Model.parse_raw(pt))
    assert pt == dt


@pytest.mark.asyncio
async def test_encrypt_decrypt_str(
    keychain: ApplicationKeychain,
):
    pt = "foo"
    ct = await keychain.encrypt(pt)
    dt = await keychain.decrypt(ct, parser=lambda _, pt: bytes.decode(pt))
    assert pt == dt


@pytest.mark.asyncio
async def test_hmac_str(
    keychain: ApplicationKeychain,
):
    await keychain.create_hmac('foo')