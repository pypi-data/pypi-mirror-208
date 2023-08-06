# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import AsyncGenerator

import fastapi

import cbra.core as cbra
from ..types import FatalAuthorizationException
from ..types import IAuthorizationServerStorage
from ..types import IExternalAuthorizationState
from ..types import OIDCProvider
from .localclientprovider import ClientProvider
from .localclientprovider import LocalClientProvider
from .localauthorizationrequeststate import LocalAuthorizationRequestState


__all__: list[str] = ['LocalOpenIdProvider']


async def get(
    state: IExternalAuthorizationState = LocalAuthorizationRequestState,
    clients: ClientProvider = LocalClientProvider,
    storage: IAuthorizationServerStorage = cbra.instance(
        name='_AuthorizationServerStorage'
    ),
) -> AsyncGenerator[OIDCProvider, None]:
    client = await clients.get(str(state.client_id))
    if client is not None:
        provider = client
    else:
        client = await storage.fetch(state.client_id)
        if client is None:
            raise FatalAuthorizationException(
                "The client specified by the request does not exist."
            )
        provider = client.get_provider()
    async with provider:
        yield provider


LocalOpenIdProvider: OIDCProvider = fastapi.Depends(get)