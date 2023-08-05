# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Awaitable
from typing import Callable
from typing import TypeAlias
from typing import Union

import pydantic
from headless.ext.oauth2.models import TokenResponse

from .authorizationcodegrant import AuthorizationCodeGrant
from .clientcredentialsgrant import ClientCredentialsGrant
from .refreshtokengrant import RefreshTokenGrant


GrantType: TypeAlias = Union[
    AuthorizationCodeGrant,
    ClientCredentialsGrant,
    RefreshTokenGrant
]


class Grant(pydantic.BaseModel):
    __root__: GrantType

    def handle(
        self,
        handler: Callable[[GrantType], Awaitable[TokenResponse]]
    ) -> Awaitable[TokenResponse]:
        return handler(self.__root__)