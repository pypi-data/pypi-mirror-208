# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio

import pytest

from cbra.core.translation import LanguageContext


@pytest.mark.asyncio
async def test_activate():
    async def f():
        LanguageContext.activate('foo')
    assert LanguageContext.get() == 'en'
    await f()
    assert LanguageContext.get() == 'foo'


@pytest.mark.asyncio
async def test_activate_nested():
    LanguageContext.activate('foo')
    assert LanguageContext.get() == 'foo'
    with LanguageContext('en'):
        assert LanguageContext.get() == 'en'
    assert LanguageContext.get() == 'foo'


@pytest.mark.asyncio
async def test_nested_translations():
    assert LanguageContext.get() == 'en'

    async def f1():
        assert LanguageContext.get() == 'nl'
        with LanguageContext('en'):
            assert LanguageContext.get() == 'en'
        assert LanguageContext.get() == 'nl'

    with LanguageContext('nl'):
        assert LanguageContext.get() == 'nl'
        await f1()
        assert LanguageContext.get() == 'nl'


@pytest.mark.asyncio
async def test_concurrent():
    assert LanguageContext.get() == 'en'

    async def f1():
        with LanguageContext('foo'):
            await asyncio.sleep(1)
            assert LanguageContext.get() == 'foo'


    async def f2():
        async def f2_n1():
            assert LanguageContext.get() == 'bar'
            with LanguageContext('baz'):
                assert LanguageContext.get() == 'baz'
            assert LanguageContext.get() == 'bar'

        await asyncio.sleep(0.5)
        with LanguageContext('bar'):
            assert LanguageContext.get() == 'bar'
            await f2_n1()

    async def f3():
        await asyncio.sleep(0.25)
        assert LanguageContext.get() == 'en'

    await asyncio.gather(f1(), f2(), f3())