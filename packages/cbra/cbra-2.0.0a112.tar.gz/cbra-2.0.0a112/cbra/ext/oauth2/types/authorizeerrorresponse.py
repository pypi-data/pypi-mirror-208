# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import NoReturn

import pydantic

from .authorizationstate import AuthorizationState
from cbra.types import IDependant


class AuthorizeErrorResponse(pydantic.BaseModel, IDependant):
    error: str = pydantic.Field(
        default=...
    )

    error_description: str | None = pydantic.Field(
        default=None
    )

    error_uri: str | None = pydantic.Field(
        default=None
    )

    state: AuthorizationState = pydantic.Field(
        default=...
    )

    def raise_exception(self) -> NoReturn:
        raise NotImplementedError