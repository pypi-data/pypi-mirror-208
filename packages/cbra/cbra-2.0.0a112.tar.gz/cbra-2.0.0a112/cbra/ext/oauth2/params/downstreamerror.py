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
from cbra.types import IDependant
from ..types import RedirectURI


DEFAULT_FRONTEND_ERROR_PAGE: str = '/error'


__all__: list[str] = [
    'DownstreamError'
]


class Error(IDependant, Abortable):
    error: str
    request: fastapi.Request
    return_url: RedirectURI | None = None

    def __init__(
        self,
        request: fastapi.Request,
        error: str,
        return_url: str | RedirectURI | None
    ):
        if return_url is not None and str.startswith(return_url, '/'):
            return_url = RedirectURI(
                f'{request.url.scheme}://{request.url.netloc}{return_url}'
            )
        if isinstance(return_url, str):
            return_url = RedirectURI(return_url)
        self.error = error
        self.return_url = return_url

    @classmethod
    def __inject__(cls): # type: ignore
        return cls.fromrequest
    
    @classmethod
    def fromrequest(
        cls,
        request: fastapi.Request,
        error: str | None = fastapi.Query(
            default=None,
            title="Error code",
            description=(
                "The error code returned by the authorization server if "
                "the user cancelled the request, refused consent, or "
                "failed to authenticate."
            )
        ),
        return_url: str | None = fastapi.Cookie(
            default=None,
            alias='oauth2.return_url',
            title="Return URL",
            description=(
                "A return URL where the server can redirect the user agent in "
                "case of an error."
            )
        )
    ):
        return cls(request, error, return_url=return_url) if error else None

    async def as_response(self) -> fastapi.Response:
        assert self.return_url is not None
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=self.return_url.redirect(allow_params=True, error=self.error)
        )


DownstreamError: Error | None = Error.depends()