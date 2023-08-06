# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from headless.ext.oauth2 import Client
from headless.ext.oauth2.types import ResponseMode
from headless.ext.oauth2.types import ResponseType

import cbra.core as cbra
from ...params import ClientStorage
from ...types import IFrontendStorage
from ...types import AuthorizationState



class BaseAuthorizationEndpoint(cbra.Endpoint):
    """A :class:`~cbra.core.Endpoint` implementation for endpoints
    that initiate an OAuth 2.x/OpenID Connect authorization request.
    """
    __module__: str = 'cbra.ext.oauth2.client'
    callback_endpoint: str
    default_response_mode: str = ResponseMode.query.value
    storage: IFrontendStorage = ClientStorage

    def get_return_uri(self) -> str:
        """Return the URI to which the callback endpoint must redirect
        after succesfully obtaining the token from the authorization
        server.
        """
        return '/'

    def get_redirect_uri(self) -> str:
        """Return the URI to which the authorization server must redirect after
        the request is authorized.
        """
        return str(self.request.url_for(self.callback_endpoint))

    async def get(self) -> fastapi.Response:
        """Initiate an OAuth 2.x/OpenID Connect authorization request
        with default parameters provided by the server.
        """
        async with await self.get_client() as client:
            assert client.client_id is not None
            params = AuthorizationState.new(
                client_id=client.client_id,
                redirect_uri=self.get_redirect_uri(),
                response_mode=ResponseMode.query,
                response_type=ResponseType.code,
                return_uri=self.get_return_uri()
            )
            await self.storage.persist(params)
            return fastapi.responses.RedirectResponse(
                status_code=303,
                url=await params.get_authorize_uri(client)
            )

    async def get_client(self) -> Client:
        """Return a :class:`headless.ext.oauth2.Client` instance that can exchange
        the authorization code.
        """
        raise NotImplementedError