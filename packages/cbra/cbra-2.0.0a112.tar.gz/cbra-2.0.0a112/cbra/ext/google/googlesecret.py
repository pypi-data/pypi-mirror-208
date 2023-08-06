# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

from google.cloud import secretmanager

from cbra.ext import secrets


class GoogleSecret(secrets.Secret):
    provider: Literal['google']
    project: str
    name: str
    value: str | None = None
    version: str = 'latest'

    def get_value(self) -> str:
        assert self.value is not None
        return self.value


async def load(secret: GoogleSecret) -> GoogleSecret:
    client = secretmanager.SecretManagerServiceAsyncClient()
    name = f'projects/{secret.project}/secrets/{secret.name}/versions/{secret.version}'
    response = await client.access_secret_version(request={'name': name}) # type: ignore
    secret.value = bytes.decode(response.payload.data, 'utf-8')
    return secret


secrets.register('google', load)
