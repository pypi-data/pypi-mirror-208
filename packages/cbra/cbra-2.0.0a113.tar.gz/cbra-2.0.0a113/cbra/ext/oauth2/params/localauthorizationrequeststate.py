# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

import cbra.core as cbra
from ..types import ExtAuthorizationRequestState
from ..types import FatalAuthorizationException
from ..types import IAuthorizationServerStorage
from ..types import IExternalAuthorizationState


__all__: list[str] = [
    'LocalAuthorizationRequestState'
]


async def get(
    storage: IAuthorizationServerStorage = cbra.instance(
        name='_AuthorizationServerStorage'
    ),
    state: ExtAuthorizationRequestState | None = fastapi.Query(
        default=None,
        title='State',
        description=(
            'An opaque value used by the client to maintain state '
            'between the request and callback. The authorization '
            'server includes this value when redirecting the '
            'user-agent back to the client. If supplied, this '
            'parameter **must** equal the `state` parameter used when '
            'creating the authorization request. The `state` parameter '
            'is ignored when using JARM because it is included in the '
            'JSON Web Token supplied using the `jwt` parameter per '
            'chosen response mode.'
        )
    ),
):
    if state is None:
        raise FatalAuthorizationException("The state parameter is missing or invalid.")
    current = await storage.fetch(state)
    if current is None:
        raise FatalAuthorizationException("The state parameter is missing or invalid.")
    return current


LocalAuthorizationRequestState: IExternalAuthorizationState = fastapi.Depends(get)