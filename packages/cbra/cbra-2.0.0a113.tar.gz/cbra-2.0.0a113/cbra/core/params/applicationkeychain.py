# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
from ckms.core import Keychain
from ckms.core import parse_dsn
from ckms.core import parse_spec

from cbra.core.conf import settings


keychain: Keychain = Keychain()


async def get_application_keychain() -> Keychain:
    must_configure: bool = False
    if settings.APP_ENCRYPTION_KEY and not keychain.has('enc'):
        keychain.add('enc', parse_spec(parse_dsn(settings.APP_ENCRYPTION_KEY)))
        must_configure = True
    if settings.APP_SIGNING_KEY and not keychain.has('sig'):
        keychain.add('sig', parse_spec(parse_dsn(settings.APP_SIGNING_KEY)))
        must_configure = True
    if must_configure:
        await keychain
    return keychain


ApplicationKeychain: Keychain = fastapi.Depends(get_application_keychain)