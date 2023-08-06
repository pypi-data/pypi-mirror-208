# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest
from google.cloud.datastore import Client
from ckms.core import Keychain

from cbra.ext.security import ApplicationKeychain
from cbra.ext.google.environ import GOOGLE_DATASTORE_NAMESPACE
from cbra.ext.google.environ import GOOGLE_SERVICE_PROJECT


@pytest.fixture(scope='session')
def client() -> Client:
    if not GOOGLE_SERVICE_PROJECT or not GOOGLE_DATASTORE_NAMESPACE:
        pytest.skip("Google not configured")
    return Client(
        project=GOOGLE_SERVICE_PROJECT,
        namespace=GOOGLE_DATASTORE_NAMESPACE
    )


@pytest.fixture(scope='session')
def keychain():
    return ApplicationKeychain(Keychain())