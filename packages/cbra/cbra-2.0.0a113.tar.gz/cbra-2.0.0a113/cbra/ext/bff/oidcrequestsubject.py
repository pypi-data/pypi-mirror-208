# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext.oauth2 import OIDCToken

from cbra.core.iam import RequestSubject
from cbra.types import IRequestPrincipal


class OIDCRequestSubject(RequestSubject):
    authenticated: bool = False
    token: OIDCToken
    principal: IRequestPrincipal
    sub: str

    def __init__(
        self,
        *,
        id: str,
        token: OIDCToken,
        principal: IRequestPrincipal
    ):
        self.email = token.email
        self.principal = principal
        self.sub = id
        self.token = token

    def get_display_name(self) -> str:
        name = self.token.name
        if not self.token.name:
            if self.token.given_name and self.token.family_name:
                # TODO: not compatible with east Asian names.
                name = f'{self.token.given_name} ${self.token.family_name}'
            elif self.token.given_name or self.token.family_name:
                name = self.token.given_name or self.token.family_name
            else:
                name = self.token.email
        assert name is not None
        return name