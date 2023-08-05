# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from cbra.types import Abortable
from cbra.types import Request
from ..types import RedirectURI


class AuthorizationException(Abortable):

    def __init__(self, error: str, redirect_uri: RedirectURI) -> None:
        self.error = error
        self.redirect_uri = redirect_uri

    async def as_response(self) -> fastapi.Response:
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=self.redirect_uri.redirect(error=self.error)
        )


def get(
    request: Request,
    error: str | None = fastapi.Query(
        default=None,
        title="Error",
        description="A code describing an error condition."
    ),
    redirect_uri: str = fastapi.Cookie(
        default=...,
        title="Redirect URI",
        alias='bff.redirect_uri',
        description=(
            "The URI to redirect the user-agent to after completing the "
            "login."
        )
    )
) -> AuthorizationException | None:
    if error is not None:
        if redirect_uri.startswith('/'):
            redirect_uri = f'{request.url.scheme}://{request.url.netloc}{redirect_uri}'
        return AuthorizationException(error, RedirectURI(redirect_uri))
    

FrontendError: AuthorizationException | None = fastapi.Depends(get)