# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from headless.ext.oauth2.models import ClaimSet

from ..types import ClientInfo
from ..types import RequestedScope


class CurrentAuthorizationRequest(pydantic.BaseModel):
    """Encapsulates information regarding an authorization request with the
    intended audience being the :term:`Resource Owner`.
    """
    request_id: str
    client: ClientInfo
    consent: list[RequestedScope]
    email: str | None
    scope: list[RequestedScope]
    id_token: ClaimSet
    requires: set[str]