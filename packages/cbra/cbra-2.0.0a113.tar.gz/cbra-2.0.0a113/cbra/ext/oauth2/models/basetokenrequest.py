# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from ..types import RFC9068AccessToken
from ..types import IAuthorizationServerStorage
from ..types import IssuedAccessToken


class BaseTokenRequest(pydantic.BaseModel):

    async def register_issued_access_token(
        self,
        sub: int | str,
        token: RFC9068AccessToken,
        signed: str,
        scope: list[str],
        storage: IAuthorizationServerStorage,
        claims: dict[str, Any]
    ) -> None:
        """Registers the access token as being issued, so that it
        can be later revoked or introspected.
        """
        issued = IssuedAccessToken.parse_rfc9068(
            token,
            claims=claims,
            scope=scope,
            signed_token=signed,
            sub=sub
        )
        await storage.persist(issued)