# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi
from headless.ext import oauth2
from headless.types import IClient

from cbra.core.conf import settings
from cbra.types import NotAuthorized
from cbra.types import NotFound
from ..types import IFrontendStorage
from ..types import ManagedGrantIdentifier
from .applicationclient import ApplicationClient
from .clientstorage import ClientStorage


async def get(
    client: oauth2.Client = ApplicationClient,
    storage: IFrontendStorage = ClientStorage,
    grant_id: ManagedGrantIdentifier | None = fastapi.Cookie(
        default=None,
        title="Grant ID",
        alias='bff.grant',
        description=(
            "Identifies the grant that is usesd to exchange tokens with "
            "the authorization server."
        )
    ),
    resource: str = fastapi.Path(
        default=...
    ),
    path: str = fastapi.Path(
        default=...
    )
):
    path = path or '/'
    spec = settings.OAUTH2_RESOURCE_SERVERS.get(resource)
    if spec is None:
        raise NotFound
    resource = spec['resource']
    if grant_id is None:
        raise NotAuthorized(
            headers={'WWW-Authenticate': 'authorization_code'}
        )
    grant = await storage.get(grant_id)
    if grant is None:
        raise NotAuthorized(
            headers={'WWW-Authenticate': 'authorization_code'}
        )
    async with await grant.get_resource_client(storage, client, resource, spec.get('scope'))\
    as resource_client:
        yield resource_client


RequestedResourceServerClient: IClient[Any, Any] = fastapi.Depends(get)

