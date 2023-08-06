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
from ..types import FatalAuthorizationException
from ..types import IAuthorizationRequest
from ..types import IAuthorizationServerStorage
from ..types import IExternalAuthorizationState
from .localauthorizationrequeststate import LocalAuthorizationRequestState


__all__: list[str] = [
    'LocalStorageAuthorizationRequest'
]


async def get(
    storage: IAuthorizationServerStorage = cbra.instance(
        name='_AuthorizationServerStorage'
    ),
    state: IExternalAuthorizationState = LocalAuthorizationRequestState
):
    authnrequest = await storage.fetch(state.request_id)
    if authnrequest is None:
        raise FatalAuthorizationException(
            f"The authorization request (id: {state.request_id}) does not "
            "exist, is expired, or otherwise not processable."
        )
    return authnrequest


LocalStorageAuthorizationRequest: IAuthorizationRequest = fastapi.Depends(get)